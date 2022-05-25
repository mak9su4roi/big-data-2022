#! /bin/bash

docker network create kafka-network
docker build broker -t broker:1.0

docker run  --rm --name keeper              \
            --network kafka-network         \
            -e ALLOW_ANONYMOUS_LOGIN=yes    \
            -d bitnami/zookeeper:3.7

docker run  --rm --name broker                          \
            --network kafka-network                     \
            -e KAFKA_CFG_ZOOKEEPER_CONNECT=keeper:2181  \
            -e ALLOW_PLAINTEXT_LISTENER=yes             \
            -d broker:1.0