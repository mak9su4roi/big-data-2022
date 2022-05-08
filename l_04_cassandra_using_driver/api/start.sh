#! /bin/bash
declare -i res=1
while [ $res -ne 0 ]; do
    sleep 10
    python3 -c "from common.session import session;session('${C_NODE}',${C_PORT},'${C_KEYSPACE}');exit(0)"
    res=${?}
done
echo "START API"
uvicorn api:app --host 0.0.0.0 --reload --port 8080