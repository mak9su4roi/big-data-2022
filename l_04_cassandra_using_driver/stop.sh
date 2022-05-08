#! /bin/bash

source ./node.env

docker kill ${C_NODE}
docker kill ${C_API}
docker network rm ${C_NETWORK}