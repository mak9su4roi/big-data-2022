#! /bin/env bash

declare -ri DEBUG=1
declare -ri OUTPUT=1

include="$(dirname "${0}")"
. "${include}/data.sh"
. "${include}/common.sh"

main()
{
  query="
  USE ${KSPACE};
  INSERT INTO ${TSONGS} (${TSONGS_ID}, ${TSONGS_AUTHOR}, ${TSONGS_NAME}, ${TSONGS_YEAR})
  VALUES (1, 'Yoh Kamiyama', 'Yellow', 2019);
  INSERT INTO ${TSONGS} (${TSONGS_ID}, ${TSONGS_AUTHOR}, ${TSONGS_NAME}, ${TSONGS_YEAR})
  VALUES (2, 'Yui Ninomiya', 'Dark seeks light', 2021);
  INSERT INTO ${TSONGS} (${TSONGS_ID}, ${TSONGS_AUTHOR}, ${TSONGS_NAME}, ${TSONGS_YEAR})
  VALUES (3, 'Ado', 'READYMADE', 2020);
  SELECT * FROM ${TSONGS};
  
  INSERT INTO ${TMOVIES} (${TMOVIES_ID}, ${TMOVIES_NAME}, ${TMOVIES_AUTHOR}, ${TMOVIES_YEAR})
  VALUES (1, 'Violet Evergarden: The Movie', 'Shinichirō Hatta', 2020);
  INSERT INTO ${TMOVIES} (${TMOVIES_ID}, ${TMOVIES_NAME}, ${TMOVIES_AUTHOR}, ${TMOVIES_YEAR})
  VALUES (2, 'I Want to Eat Your Pancreas', 'Keiji Mita', 2018);
  INSERT INTO ${TMOVIES} (${TMOVIES_ID}, ${TMOVIES_NAME}, ${TMOVIES_AUTHOR}, ${TMOVIES_YEAR})
  VALUES (3, 'Your Name', 'Kōichirō Itō', 2016);
  SELECT * FROM ${TMOVIES};"
  if from_compose ${NODES[0]}; then
    run docker-compose exec ${NODES[0]} cqlsh -e "${query}"
  else
    run docker exec -it ${NODES[0]} cqlsh -e "${query}"
  fi
}

main
