#! /bin/env bash

run()
{
  if ((DEBUG==1)); then
    echo RUN "[ ${@} ]"
  fi
  if ((OUTPUT==1)); then
    "${@}"
  else
    "${@}" &>/dev/null
  fi
  return $?
}

from_compose()
{
  docker-compose exec ${1} sleep 0
}
