#! /bin/bash

docker-compose exec spark-worker bash -c 'spark-submit --master "${SPARK_MASTER_URL}" --deploy-mode client /opt/app/reader/main.py'