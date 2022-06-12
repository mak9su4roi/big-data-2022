CREATE KEYSPACE l_08 WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': 1
};
USE l_08;

--- All transaction here are fraud and initiate by user with uid @uid
CREATE TABLE initiated_fraud_transaction (
    uid 	            text,
    amount  			float,
	transaction_date    date,
    PRIMARY KEY ((uid), amount, transaction_date)
);

--- All transaction here are initiate by user with uid @uid
CREATE TABLE initiated_transaction_by_amount (
    uid 	    	    text,
    amount  	        float,
	transaction_date    date,
    PRIMARY KEY ((uid), amount, transaction_date)
) WITH CLUSTERING ORDER BY (amount DESC);


--- All transaction here are received by user with uid @uid
CREATE TABLE received_transaction_by_date (
    uid                 text,
	transaction_date    date, 
	amount              float,
    PRIMARY KEY((uid), transaction_date, amount)
) WITH CLUSTERING ORDER BY (transaction_date DESC);;