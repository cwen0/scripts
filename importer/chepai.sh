#!/bin/bash
if  [ $# != 3 ];  then
    echo "Usage: $0 port count tableName"
    exit 1
fi

port=$1
count=$2
tableName=$3

importer -t "CREATE TABLE ${tableName}(id bigint(21),name varchar(10) DEFAULT NULL,number varchar(7) DEFAULT NULL,city int(11) DEFAULT NULL,nation int(11) DEFAULT NULL,PRIMARY KEY (id),KEY cp (number))" \
       -h  127.0.0.1  -P ${port} -D test  \
       -n ${count}  \
       -c 100 -b 100
