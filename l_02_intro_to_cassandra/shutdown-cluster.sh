#! /bin/env bash

declare -ri OUTPUT=0
declare -ri DEBUG=1

src_dir="$(dirname "${0}")"
. "${src_dir}/data.sh"
. "${src_dir}/common.sh"

rm_node()
{
  run docker kill ${1}
  return $?
}

rm_net()
{
  run docker network rm ${1}
  return $?
}

main()
{
  for node in "${NODES[@]}"; do 
    if rm_node ${node}; then
      echo "killed container ${node}"
    else
      echo "ERROR: failed to kill container ${node}"
    fi
  done
  if rm_net ${NET}; then
    echo "removed network ${NET}"
  else
    echo "ERROR: failed to remove network ${NET}"
  fi
}

main
