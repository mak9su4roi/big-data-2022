from calendar import calendar
from kafka import KafkaProducer
from datetime import datetime, timedelta
from time import sleep, perf_counter
from argparse import ArgumentParser
import logging
import json
import pandas as pd
from calendar import monthrange
from random import randint

def gen_date() -> str:
    n = datetime.now()
    return datetime.strftime(n - timedelta(days=randint(0, monthrange(n.year, n.month)[1]-1))
                - timedelta(hours=randint(0, 23))
                - timedelta(minutes=randint(0, 59))
                - timedelta(seconds=randint(0, 59))
                - timedelta(microseconds=randint(0, 9_999_99)), '%Y-%m-%d %H:%M:%S.%f')

def brk_connect(name: str, port: str) -> KafkaProducer:
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=f"{name}:{port}",
                                    value_serializer=lambda r: json.dumps({
                                        "transaction_date": gen_date(),
                                        "step": str(r.step),
                                        "type": str(r.type),
                                        "amount": str(r.amount),
                                        "nameOrig": str(r.nameOrig),
                                        "oldbalanceOrg": str(r.oldbalanceOrg),
                                        "newbalanceOrig": str(r.newbalanceOrig),
                                        "nameDest": str(r.nameDest),
                                        "oldbalanceDest": str(r.oldbalanceDest),
                                        "newbalanceDest": str(r.newbalanceDest),
                                        "isFraud": str(r.isFraud)
                                    }).encode("utf-8")
            )
            logging.warning(f"Connected to {name}:{port}")
            return producer
        except Exception as err:
            logging.error(err)

def send_msg(producer: KafkaProducer, msg: str, min_wait: float) -> None:
    s_ = perf_counter()
    producer.send("transactions", msg)
    d_ = perf_counter() - s_
    if (d_ < min_wait):
        sleep((min_wait - d_)*.9)

def stream(t, ulb):
    s_, ind = perf_counter(), 0
    while perf_counter() - s_ < t and ind < ulb:
        yield ind
        ind+=1

def main():
    p = ArgumentParser(description="Stream twitts with Kafka")
    p.add_argument('T', type=int, help='Time: number of seconds to stream twitts')
    p.add_argument('HZ', type=int, help='Frequency: twitts per second')
    a = p.parse_args()

    df = pd.read_csv("PS_20174392719_1491204439457_log.csv")
    producer = brk_connect("broker", "9092") 
    [send_msg(producer, df.iloc[ind], 1/a.HZ) for ind in stream(a.T, len(df))]

if __name__ == "__main__":
    main()