CREATE KEYSPACE l_03 WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': 3
};
USE l_03;

-- table for Q{3,5}
CREATE TABLE review_body_and_pos_reviews_by_customer_id (
    customer_id     text,
    review_id       text,
    review_body     text,
    pos_reviews     int STATIC,
    PRIMARY KEY((customer_id), review_id)
);

-- table for Q{1,2}
CREATE TABLE review_body_by_product_id_and_star_rating (
    product_id      text,
    star_rating     int,
    review_id       text,
    review_body     text,
    PRIMARY KEY((product_id), star_rating, review_id)
);

-- table for Q4
CREATE TABLE customer_id_by_product_id_and_reviews_number (
    product_id      text,
    all_reviews     int,
    customer_id     text,
    PRIMARY KEY((product_id), all_reviews, customer_id)
);