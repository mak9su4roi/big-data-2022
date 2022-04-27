USE l_03;

-- Q1
SELECT review_body
FROM review_body_by_product_id_and_star_rating
    WHERE product_id = '0553380958';

-- Q2
SELECT review_body
FROM review_body_by_product_id_and_star_rating
    WHERE product_id = '0553380958'
        AND star_rating = 4;

-- Q3
SELECT review_body
FROM review_body_and_pos_reviews_by_customer_id
    WHERE customer_id = '51357452';

-- Q4
SELECT customer_id
FROM customer_id_by_product_id_and_reviews_number
    WHERE product_id = '1560371854'
        AND all_reviews > 20;

-- Q5
SELECT pos_reviews
FROM review_body_and_pos_reviews_by_customer_id
    WHERE customer_id = '50732546'
    LIMIT 1;