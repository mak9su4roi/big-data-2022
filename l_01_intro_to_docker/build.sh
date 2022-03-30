#! /bin/env bash

readonly ERROR="\033[0;31mERROR\033[0m"
readonly SUCCESS="\033[0;32mSUCCESS\033[0m"


main() {
    if [[ "$#" -ne 1 ]]; then
        >&2 echo -e "${ERROR}: one arguemt required (image name)"
        return 1
    fi
    docker build . -t ${1}
    if [[ $? -eq 0 ]]; then
        echo -e "${SUCCESS}: image $1 built"
        return 0
    fi
    return 1
}

main $@