# Lab III: Cassandra data modeling


## Requirements
...

## Setup

-   ```bash
    git clone https://github.com/mak9su4roi/big-data-2022
    ```
-   ```bash
    cd ./big-data-2022/l_03_cassandra_data_modeling
    ```

## Columns 

- `customer_id` -- random identifier that can be used to aggregate reviews written by a single author. 
- `productid` -- the unique Product ID the review pertains to.
- `start_rating` -- the 1-5 star rating of the review.
- `review_id` -- the unique ID of the review.
- `review_body` -- the review text.
- `pos_reviews` -- the number of positive reviews (4 and 5 starts) that customer left. Calculated for each `customer_id` before filling DB.
- `all_reviews` -- the number of reviews that customer left. Calculated for each `customer_id` before filling DB;

## Design of Tables per Query

### $Q_1$ & $Q_2$ 

| column_name | data_type | column_type | 
| ----------- | --------- | ----------- |
| product_id  | text      | K			|
| star_rating | int       | C(ASC)      |
| review_id   | text      | C(ASC)      |
| review_body | text      |             |

Both $Q_{1,2}$ use `product_id` (Partition Key) for filtering.

---

### $Q_3$ & $Q_5$

| column_name          | data_type | column_type | 
| -------------------- | --------- | ----------- |
| customer_id 		   | text      | K			 |
| review_id   		   | text      | C(ASC)      |
| review_body 		   | text      |             |
| pos_reviews          | int       | S           |

Both $Q_{3,5}$ user `customer_id` (Partition Key) for filtering. As long as `pos_reviews` is in common for each partition, it should be static.

---

### $Q_4$

| column_name      | data_type | column_type | 
| ---------------- | --------- | ----------- |
| product_id       | text      | K			 |
| all_reviews      | int       | C(ASC)      |
| customer_id      | text      | C(ASC)      |

$Q_4$ does not use `star_rating` (Clustering Key) for filtering and $Q_{1,2}$ does not use `all_reviews` (Clustering Key) for filtering, so they should be separate tables.

---
## Tables & Queries

### Launch Cluster

```bash
docker-compose up -d n{1..3}
```

### Create Tables

```bash
docker-compose exec n1 cqlsh -e "$(cat ddl.cql)"
```

### Fill Tables Somehow
```bash
...
```

### Query Tables
```bash
docker-compose exec n1 cqlsh -e "$(cat query.cql)"
```

### Shutdown Cluster

```bash
docker-compose down
```
