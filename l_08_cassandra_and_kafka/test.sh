#! /bin/bash

echo "======================================="
echo "---"

request() {
    echo "url: ${1}"
    printf "response: "
    curl -s -X GET "${1}" | jq .
    echo "---"
}

echo "<QueryN: 1>"
request "http://localhost:8080/frauds/initiated_by/C1971684490"
request "http://localhost:8080/frauds/initiated_by/XXX"

echo "======================================="
echo "---"

echo "<QueryN: 2>"
request "http://localhost:8080/transactions/initiated_by/C363736674"
request "http://localhost:8080/transactions/initiated_by/C999741107"
request "http://localhost:8080/transactions/initiated_by/C1000001337"
request "http://localhost:8080/transactions/initiated_by/C3637366"

echo "======================================="
echo "---"

echo "<QueryN: 3>"
request "http://localhost:8080/transactions-sum/received_by/C601893033?from_=2022-05-12&to_=2022-06-11" 
request "http://localhost:8080/transactions-sum/received_by/C601893033?from_=2022-05-19&to_=2022-06-01" 
request "http://localhost:8080/transactions-sum/received_by/C601893033?from_=2022-06-01&to_=2022-07-11" 
request "http://localhost:8080/transactions-sum/received_by/C601893033?from_=2022-07-01&to_=2022-07-11" 

echo "======================================="