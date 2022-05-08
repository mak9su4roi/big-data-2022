#! /bin/bash
declare -i res=1
declare args="'${C_NODE}',${C_PORT},'${C_KEYSPACE}'"
while [ $res -ne 0 ]; do
    sleep 10
    echo $args
    python3 -c "from common.session import session;session(${args});exit(0)"
    res=${?}
done
echo "START LOADER"
python3 loader.py "${@}"
echo "LOADER is FINISHED"