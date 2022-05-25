#! /bin/bash

docker kill broker
docker kill keeper
docker network rm kafka-network