from kafka import KafkaConsumer
import logging
import json
import pandas as pd

def brk_connect(name: str, port: str) -> KafkaConsumer:
    while True:
        try:
            producer = KafkaConsumer("tweets",
                                    bootstrap_servers=f"{name}:{port}",
                                    value_deserializer=lambda s: pd.Series(json.loads(s.decode("utf-8"))),
                                    consumer_timeout_ms=10000
            )
            logging.warning(f"Connected to {name}:{port}")
            return producer
        except Exception as err:
            logging.error(err)

def fstream(consumer: KafkaConsumer) -> list[pd.DataFrame, str]:
    mm_, slist = None, [] 
    for msg in consumer:
        msg = msg.value
        (DD, MM, YY), (hh, mm, _, _) = map(lambda s: s.split(":") if ":" in s else s.split("-"), msg.created_at.split("::"))
        if mm_ is None:
            DD_, MM_, YY_, hh_, mm_ = DD, MM, YY, hh, mm
        if mm_ != mm:
            yield pd.DataFrame(slist), f"tweets_{DD_}_{MM_}_{YY_}_{hh_}_{mm_}"
            DD_, MM_, YY_, hh_, mm_ = DD, MM, YY, hh, mm
            slist.clear()
        slist += [msg]
    yield pd.DataFrame(slist), f"tweets_{DD_}_{MM_}_{YY_}_{hh_}_{mm_}"

def main():
    for fl, fn in fstream(brk_connect("broker", "9092")):
       fl.to_csv(f"data/{fn}")

if __name__ == "__main__":
    main()