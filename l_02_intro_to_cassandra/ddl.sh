#! /bin/env bash

declare -ri OUTPUT=1
declare -ri DEBUG=1

include="$(dirname "${0}")"
. "${include}/data.sh"
. "${include}/common.sh"

main()
{
  declare -r query="
  CREATE KEYSPACE ${KSPACE} WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1 };
  USE ${KSPACE};
  CREATE TABLE ${TSONGS} (
    ${TSONGS_ID} int,
    ${TSONGS_AUTHOR} text,
    ${TSONGS_NAME} text,
    ${TSONGS_YEAR} int,
    PRIMARY KEY (${TSONGS_ID})
  );
  CREATE TABLE ${TMOVIES} (
    ${TMOVIES_ID} int,
    ${TMOVIES_NAME} text,
    ${TMOVIES_AUTHOR} text,
    ${TMOVIES_YEAR} int,
    PRIMARY KEY (${TSONGS_ID})
  );
  DESCRIBE TABLES"
  if from_compose ${NODES[0]}; then
    run docker-compose exec ${NODES[0]} cqlsh -e "${query}"
  else
    run docker exec -it ${NODES[0]} cqlsh -e "${query}"
  fi
}

main
