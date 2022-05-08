from fastapi import FastAPI
from common.session import session
import pandas as pd
import os
from datetime import date
from string import Template
from time import time

app = FastAPI()
sessions = { n: {"prs": [n, os.environ["C_PORT"], os.environ["C_KEYSPACE"]], "handle": None} for n in [os.environ["C_NODE"]] }

Q1 = "SELECT review_body FROM review_body_by_product_id_and_star_rating WHERE product_id = ?"
Q2 = "SELECT review_body FROM review_body_by_product_id_and_star_rating WHERE product_id = ? AND star_rating >= ?"
Q3 = "SELECT review_body FROM review_body_by_customer_id WHERE customer_id = ? "
Q4 = Template("SELECT product, all_reviews FROM all_reviews_by_time_period WHERE year in ${itv} AND review_date >= ? AND review_date <= ? ")
Q5 = Template("SELECT customer_id, ver_reviews FROM ver_pos_neg_reviews_by_time_period WHERE year in ${itv} AND review_date >= ? AND review_date <= ? ")
Q6 = Template("SELECT customer_id, pos_reviews FROM ver_pos_neg_reviews_by_time_period WHERE year in ${itv} AND review_date >= ? AND review_date <= ? ")
Q7 = Template("SELECT customer_id, neg_reviews FROM ver_pos_neg_reviews_by_time_period WHERE year in ${itv} AND review_date >= ? AND review_date <= ? ")

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

@app.get("/reviews/product/{id_}")
def q1_q2(id_: str, star_rating: int | None = None):
    msg = f"No review of product wiht <product_id> {id_}"
    match star_rating:
        case int(star_rating):
            msg = f"No review of poduct with <product_id> {id_} and <start_rating> higher or equal {star_rating}"
            return (Try((Q2, id_, star_rating), msg)
                    & (lambda x: cassandra_get_df(*x))
                    & (lambda df: df["review_body"])
                ).get()
        case _:
            return Try(cassandra_get_df(Q1, id_), msg).get()

@app.get("/reviews/customer/{id_}")
def q3(id_: str):
    msg = f"Customer with <custmoer_id> {id_} has written no reviews"
    return (Try ((Q3, id_), msg)
        & (lambda x: cassandra_get_df(*x))
    ).get()

def q4_q5_q6_q7(q: Template, key_col: str, val_col: str, msg: str, from_: date, to_: date, N: int | None = None):
    itv = f"({', '.join(map(str, range(from_.year, to_.year+1)))})"
    return (Try((q.substitute(itv=itv), from_, to_), msg)
        & (lambda x: cassandra_get_df(*x))
        & (lambda df: df.groupby(key_col).sum(val_col).sort_values(by=[val_col], ascending=False).reset_index())
        & (lambda df: df if N is None else df[:N])
        & (lambda df: df.apply(lambda df: [df[key_col], int(df[val_col])], axis=1))
    ).get()

@app.get("/items/")
def q4(from_: date, to_: date, N: int | None = None ):
    msg = f"No item was reviewed from {from_} to {to_}"
    return q4_q5_q6_q7(Q4, "product", "all_reviews", msg, from_, to_, N)

@app.get("/productive-customers/")
def q5(from_: date, to_: date, N: int | None = None ):
    msg = f"No productive customer from {from_} to {to_}"
    return q4_q5_q6_q7(Q5, "customer_id", "ver_reviews", msg, from_, to_, N)

@app.get("/productive-backers/")
def q6(from_: date, to_: date, N: int | None = None ):
    msg = f"No productive backers from {from_} to {to_}"
    return q4_q5_q6_q7(Q6, "customer_id", "pos_reviews", msg, from_, to_, N)

@app.get("/productive-haters/")
def q7(from_: date, to_: date, N: int | None = None ):
    msg = f"No productive haters from {from_} to {to_}"
    return q4_q5_q6_q7(Q7, "customer_id", "neg_reviews", msg, from_, to_, N)