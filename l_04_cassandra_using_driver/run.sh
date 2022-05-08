#! /bin/bash

source ./node.env

docker build api -t ${C_API}
docker build loader -t ${C_LOADER}
docker build node -t ${C_NODE}

docker network create ${C_NETWORK}

docker run --rm --name ${C_NODE}                    \
                            --env-file node.env     \
                            --network ${C_NETWORK}  \
                            -d ${C_NODE}

docker run --rm --name ${C_LOADER}                                      \
                            -v "${PWD}/loader.py:/usr/src/loader.py:ro" \
                            -v "${PWD}/${DATASET}.tsv:/usr/src/${C_DATA}:ro" \
                            -v "${PWD}/common:/usr/src/common:ro"       \
                            --env-file node.env                         \
                            --network ${C_NETWORK}                      \
                            -d ${C_LOADER} ${C_DATA}

docker run --rm --name ${C_API} -v "${PWD}/api.py:/usr/src/api.py:ro" \
                                -v "${PWD}/common:/usr/src/common:ro" \
                                --env-file node.env                   \
                                -p 8080:8080                          \
                                --network ${C_NETWORK}                \
                                -d ${C_API} 