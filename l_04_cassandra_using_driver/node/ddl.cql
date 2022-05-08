CREATE KEYSPACE l_04 WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': 1
};
USE l_04;

-- table for Q{1,2}
CREATE TABLE review_body_by_product_id_and_star_rating (
    product_id      text,
    star_rating     int,
    review_id       text,
    review_body     text,
    PRIMARY KEY((product_id), star_rating, review_id)
);

-- table for Q3
CREATE TABLE review_body_by_customer_id (
    customer_id     text,
    review_id       text,
    review_body     text,
    PRIMARY KEY((customer_id), review_id)
);

-- table for Q4
CREATE TABLE all_reviews_by_time_period (
    year        int,
    review_date timestamp,
    product     text,
    all_reviews int,
    PRIMARY KEY((year), review_date, product)
);

-- table for Q{5..7}
CREATE TABLE ver_pos_neg_reviews_by_time_period (
    year        int,
    review_date timestamp,
    customer_id text,
    ver_reviews int,
    pos_reviews int,
    neg_reviews int,
    PRIMARY KEY((year), review_date, customer_id)
);