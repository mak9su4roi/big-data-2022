#! /bin/env bash

declare -r  NET="cassandra-net-v1"
declare -ra NODES=(n1 n2 n3)

declare -r  KSPACE="hw2_bilyk"

declare -r  TSONGS="favorite_songs"
declare -r  TSONGS_ID="id"
declare -r  TSONGS_AUTHOR="author"
declare -r  TSONGS_NAME="song_name"
declare -r  TSONGS_YEAR="release_year"

declare -r  TMOVIES="favorite_movies"
declare -r  TMOVIES_ID="id"
declare -r  TMOVIES_NAME="name"
declare -r  TMOVIES_AUTHOR="producer"
declare -r  TMOVIES_YEAR="release_year"
