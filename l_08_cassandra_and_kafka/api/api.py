import logging
from fastapi import FastAPI
from common.session import session
import pandas as pd
import os
from datetime import date
from string import Template
from time import time

app = FastAPI()
sessions = { n: {"prs": [n, "9042", "l_08"], "handle": None} for n in ["node"] }

Q1 = "SELECT * FROM initiated_fraud_transaction WHERE uid = ?"
Q2 = "SELECT * FROM initiated_transaction_by_amount WHERE uid = ? LIMIT 3;"
Q3 = "SELECT sum(amount) FROM received_transaction_by_date WHERE uid = ? AND transaction_date >= ? AND transaction_date <= ?"

def pandas_factory(colnames, rows):
    """Read the data returned by the driver into a pandas DataFrame"""
    print(len(colnames))
    return pd.DataFrame(rows, columns=colnames)

class Try:
    def __init__(self, val, default=None):
        self.__val = val
        self.__default = default
        self.__err = False

    def get(self):
        if self.__err:
            return self.__err
        if self.__val is None:
            return self.__default
        return self.__val

    def __and__(self, f):
        if self.__val is not None and self.__err == False:
            try:
                self.__val = f(self.__val)
            except Exception as e:
                self.__err = str(e)
        return self

def cassandra_get_df(q: str, *args, last_attempt=False) -> pd.DataFrame | None:
    for k, meta in sessions.items():
        handle = meta["handle"] 
        try: 
            if handle is None and last_attempt:
                handle = session(*meta["prs"])
                sessions[k]["handle"] = handle
            elif handle is None:
                continue
            prep_q = handle.prepare(q)
            t=time()
            res = pd.DataFrame(handle.execute(prep_q, args))
            return res if len(res) else None
        except Exception as e:
            sessions[k]["handle"] = None
            continue
    if not last_attempt:
        return cassandra_get_df(q, *args, last_attempt=True)
    raise Exception("Connection Error")

@app.get("/frauds/initiated_by/{uid}")
def q1(uid: str):
    logging.warning(uid)
    msg = f"No fraud transactions were initiated by user: {uid}"
    return (Try((Q1, uid), msg)
            & (lambda x: cassandra_get_df(*x))
            & (lambda df: df.apply(lambda r: {"amount": r["amount"], "transaction_date": str(r["transaction_date"])}, axis=1))
    ).get()

@app.get("/transactions/initiated_by/{uid}")
def q2(uid: str):
    logging.warning(uid)
    msg = f"No transactions were initiated by user: {uid}"
    return (Try((Q2, uid), msg)
            & (lambda x: cassandra_get_df(*x))
            & (lambda df: df.apply(lambda r: {"amount": r["amount"], "transaction_date": str(r["transaction_date"])}, axis=1))
    ).get()

@app.get("/transactions-sum/received_by/{uid}")
def q3(uid: str, from_: date, to_: date):
    msg = f"User@{uid} received no transactions from {from_} to {to_}"
    return (Try((Q3, uid, from_, to_), msg)
        & (lambda x: cassandra_get_df(*x))
        & (lambda df: df.apply(lambda r:{"transaction_sum": r["system_sum_amount"]}, axis=1))
    ).get()