from kafka import KafkaConsumer
from enum import Enum
import pandas as pd
import logging
import json

from cassandra.cluster import Session, BatchStatement, PreparedStatement, ConnectionShutdown
from cassandra import ConsistencyLevel
from l_08_cassandra_and_kafka.common.session import session
import numpy as np
import pathlib
import sys
import os

FRAME_SIZE = 200
TableTypes = Enum('TableTypes', 'FRAUD AMOUNT_N_DATE')
PRESERVE_COLUMNS = ["nameOrig", "nameDest", "amount", "transaction_date"]
REQ_COLUMNS = ["uid", "amount", "transaction_date"]

Q1_ins = (
    "INSERT INTO initiated_fraud_transaction (uid, amount, transaction_date) VALUES (?,?,?)",
    ["uid", "amount", "transaction_date"],
    [np.dtype(str), np.dtype(float), np.dtype('M')]
)

Q2_ins = (
    "INSERT INTO initiated_transaction_by_amount (uid, amount, transaction_date) VALUES (?,?,?)",
    ["uid", "amount", "transaction_date"],
    [np.dtype(str), np.dtype(float), np.dtype('M')]
)

Q3_ins = (
    "INSERT INTO received_transaction_by_date (uid, amount, transaction_date) VALUES (?,?,?)",
    ["uid", "amount", "transaction_date"],
    [np.dtype(str), np.dtype(float), np.dtype('M')]
)

def brk_connect(name: str, port: str) -> KafkaConsumer:
    while True:
        try:
            producer = KafkaConsumer("transactions",
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


def cassandra_ins_df(s: Session, df: pd.DataFrame, 
        ins: tuple[str|PreparedStatement, list[str], list[np.dtype]]) -> None:
    match ins:
        case str(cmd), list(cols), list(types):
            df = df[cols].dropna()
            prep_cmd = s.prepare(cmd)
            for c, t in zip(cols, types):       
                df[c] = df[c].astype(t)
            logging.warning(f"InsertCMD: {cmd}")
        case prep_cmd, list(cols), list(types):
            pass

    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    df.apply(lambda row: batch.add(prep_cmd, [row[col] for col in cols]), 1)
    try:
        s.execute(batch)
    except ConnectionShutdown as e: 
        logging.error(f"FatalError: {str(e)}")
        exit()
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        cassandra_ins_df(s,df.iloc[:df(len)//2],(prep_cmd, cols, types))
        cassandra_ins_df(s,df.iloc[df(len)//2:],(prep_cmd, cols, types))

def stream(consumer: KafkaConsumer):
    tns = {TableTypes.FRAUD: [], TableTypes.AMOUNT_N_DATE: []}
    for msg in consumer:
        t = msg.value[PRESERVE_COLUMNS]
        tns[TableTypes.FRAUD]   += [t] if int(msg.value.isFraud) else []
        tns[TableTypes.AMOUNT_N_DATE]  += [t] 
        for tt in tns.keys():
            if len(tns[tt]) == FRAME_SIZE: yield tt, pd.DataFrame(tns[tt]), tns[tt].clear()
    for tt in tns.keys(): yield tt, pd.DataFrame(tns[tt]), tns[tt].clear()

def main():
    ss = session("node", "9042", "l_08")
    for tt, df, _ in stream(brk_connect("broker", "9092")):
        logging.error(tt.value)
        logging.error(df)
        match(tt):
            case TableTypes.AMOUNT_N_DATE:
                cassandra_ins_df(ss, df.rename(columns={"nameOrig": "uid"})[REQ_COLUMNS], Q2_ins)
                cassandra_ins_df(ss, df.rename(columns={"nameDest": "uid"})[REQ_COLUMNS], Q3_ins)
            case TableTypes.FRAUD:
                cassandra_ins_df(ss, df.rename(columns={"nameOrig": "uid"})[REQ_COLUMNS], Q1_ins)

if __name__ == "__main__":
    main()