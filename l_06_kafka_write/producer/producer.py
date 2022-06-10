from kafka import KafkaProducer
from datetime import datetime
from time import sleep, perf_counter
from argparse import ArgumentParser
import logging
import json
import pandas as pd

def brk_connect(name: str, port: str) -> KafkaProducer:
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=f"{name}:{port}",
                                    value_serializer=lambda r: json.dumps({
                                        "time": datetime.strftime(datetime.now(),'%d-%m-%Y::%H:%M:%S:%f'),
                                        "author_id": r.author_id,
                                        "text": r.text
                                    }).encode("utf-8")
            )
            logging.warning(f"Connected to {name}:{port}")
            return producer
        except Exception as err:
            logging.error(err)

def send_msg(producer: KafkaProducer, msg: str, min_wait: float) -> None:
    s_ = perf_counter()
    producer.send("tweets", msg)
    d_ = perf_counter() - s_
    if (d_ < min_wait):
        sleep((min_wait - d_)*.9)

def stream(t):
    s_, ind = perf_counter(), 0
    while perf_counter() - s_ < t:
        yield ind
        ind+=1

def main():
    p = ArgumentParser(description="Stream twitts with Kafka")
    p.add_argument('T', type=int, help='Time: number of seconds to stream twitts')
    p.add_argument('HZ', type=int, help='Frequency: twitts per second')
    a = p.parse_args()

    df = pd.read_csv("twcs.csv")
    producer = brk_connect("broker", "9092") 
    [send_msg(producer, df.iloc[ind], 1/a.HZ) for ind in stream(a.T)]

if __name__ == "__main__":
    main()