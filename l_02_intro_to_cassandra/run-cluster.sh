#! /bin/env bash

declare -ri OUTPUT=0
declare -ri DEBUG=1

src_dir="$(dirname "${0}")"
. "${src_dir}/data.sh"
. "${src_dir}/common.sh"


net_create()
{
  run docker network create ${1}
  return $?
}

nod_create()
{
  run docker run --rm --name ${1} --network ${2} -d -e CASSANDRA_SEEDS=${3} cassandra:latest
  return $?
}

main()
{
  if net_create ${NET}; then
    echo "created network ${NET}"
  else
    echo "network ${NET} already exists"
  fi

  local seeds=$(IFS=, ; echo "${NODES[*]}")
  for node in "${NODES[@]}"
  do
    if nod_create "${node}" "${NET}" "${seeds}"; then
      echo "created container ${node}"
    else
      echo "ERROR: failed to create container ${node} ( running already | ${node} already exists )"
    fi
  done
}

main
