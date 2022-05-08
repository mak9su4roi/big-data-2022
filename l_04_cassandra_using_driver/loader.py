from cassandra.cluster import Session, BatchStatement, PreparedStatement, ConnectionShutdown
from cassandra import ConsistencyLevel
import numpy as np
import pandas as pd
from argparse import ArgumentParser, ArgumentTypeError
import pathlib
import sys
import os
from common.session import session

REQUIRED_COLS = ["product_id", "customer_id", "review_id", "star_rating", "review_body", "verified_purchase", "review_date", "product_title", "product_category"]

Q1_Q2_ins = (
    "INSERT INTO review_body_by_product_id_and_star_rating (product_id, star_rating, review_id, review_body) VALUES (?,?,?,?)",
    ["product_id", "star_rating", "review_id", "review_body"],
    [np.dtype(str), np.dtype(int), np.dtype(str), np.dtype(str)]
)
Q3_ins = (
    "INSERT INTO review_body_by_customer_id (customer_id, review_id, review_body) VALUES (?,?,?)",
    ["customer_id", "review_id", "review_body"],
    [np.dtype(str), np.dtype(str), np.dtype(str)]
)
Q4_ins = (
    "INSERT INTO all_reviews_by_time_period (year, review_date, product, all_reviews) VALUES (?, ?, ?, ?)",
    ["year", "review_date", "product", "all_reviews"],
    [np.dtype(int), np.dtype('M'), np.dtype(str), np.dtype(int)]
)
Q5_Q6_Q7_ins = (
    "INSERT INTO ver_pos_neg_reviews_by_time_period (year, review_date, customer_id, ver_reviews, pos_reviews, neg_reviews) VALUES (?, ?, ?, ?, ?, ?)",
    ["year", "review_date", "customer_id", "ver_reviews", "pos_reviews", "neg_reviews"],
    [np.dtype(int), np.dtype('M'), np.dtype(str), np.dtype(int), np.dtype(int), np.dtype(int)]
)

def read_tsv(name: str, cols: list[str]) -> pd.DataFrame:
    return pd.read_csv(name, sep="\t", on_bad_lines="warn")[cols]

def cassandra_ins_df(s: Session, df: pd.DataFrame, 
        ins: tuple[str|PreparedStatement, list[str], list[np.dtype]],
        size: int) -> None:
    is_nested = False
    match ins:
        case str(cmd), list(cols), list(types):
            df = df[cols].dropna()
            prep_cmd = s.prepare(cmd)
            for c, t in zip(cols, types):       
                df[c] = df[c].astype(t)
            processed_size, cur_progress, prv_progress = 0, 0, 0
            full_size = len(df)
            print(f"InsertCMD: {cmd}")
        case prep_cmd, list(cols), list(types):
            is_nested = True

    for chunck in np.array_split(df, len(df)//size):
        batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        chunck.apply(lambda row: batch.add(prep_cmd, [row[col] for col in cols]), 1)
        try:
            s.execute(batch)
        except ConnectionShutdown as e: 
            print(f"FatalError: {str(e)}")
            exit()
        except Exception as e:
            print(f"Error: {str(e)}")
            cassandra_ins_df(s,chunck,(prep_cmd, cols, types), size//2)
        
        if not is_nested:
            processed_size+=size
            cur_progress = processed_size/full_size
            if cur_progress - prv_progress > .025:
                prv_progress = cur_progress
                sys.stdout.write('\r')
                sys.stdout.write(f"TableSize::{full_size}::PROGRESS::{int(cur_progress*100)}%")
                sys.stdout.flush()
    if not is_nested:
        print()

def tsv_file(file: str) -> str:
    fl = pathlib.Path(file)
    if not fl.exists():
        raise ArgumentTypeError(f"{file} does not exists")
    if fl.suffix != ".tsv":
        raise ArgumentTypeError(f"{file} is not .tsv type")
    return file

def main():
    p = ArgumentParser()
    p.add_argument("file", type=tsv_file)
    p.add_argument("--csize", type=int, default=400)
    args = p.parse_args()
    print(f"file: {args.file}, chunck size: {args.csize}")

    df = read_tsv(args.file, REQUIRED_COLS)
    df["product"] = df[["product_id", "product_title"]].astype(str).apply("::".join, axis=1)
    df["year"] = df.review_date.str.split(pat="-", expand=True)[0]

    q4 = df[["year", "review_date", "product"]]
    q4 = q4.groupby(["year", "review_date", "product"]).agg(all_reviews=("product", np.size))
    q4 = q4.reset_index(level=[0,1,2])

    q5_6_7 = df[["year", "review_date", "customer_id", "star_rating", "verified_purchase"]]

    q5 = q5_6_7[q5_6_7.verified_purchase == "Y"]
    q5 = q5.groupby(["year", "review_date", "customer_id"]).agg(ver_reviews=("customer_id", np.size))

    q6 = q5_6_7[q5_6_7.star_rating >= 4]
    q6 = q6.groupby(["year", "review_date", "customer_id"]).agg(pos_reviews=("customer_id", np.size))

    q7 = q5_6_7[q5_6_7.star_rating <= 2]
    q7 = q7.groupby(["year", "review_date", "customer_id"]).agg(neg_reviews=("customer_id", np.size))

    q5_6_7 = q5
    q5_6_7["pos_reviews"] = q6["pos_reviews"]
    q5_6_7["neg_reviews"] = q7["neg_reviews"]
    q5_6_7 = q5_6_7.fillna(0).reset_index(level=[0,1,2])
    
    s = session(os.environ["C_NODE"], os.environ["C_PORT"], os.environ["C_KEYSPACE"])
    cassandra_ins_df(s, df, Q1_Q2_ins, args.csize)
    cassandra_ins_df(s, df, Q3_ins, args.csize)
    cassandra_ins_df(s, q4, Q4_ins, args.csize)
    cassandra_ins_df(s, q5_6_7, Q5_Q6_Q7_ins, args.csize)

if __name__ == "__main__":
    main()