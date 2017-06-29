#!/bin/bash
if  [ $# != 3 ];  then
    echo "Usage: $0 port passwd  count"
    exit 1
fi

port=$1
passwd=$2
count=$3

importer -t "CREATE TABLE  t(a INT(11) DEFAULT NULL,b DOUBLE DEFAULT NULL,c VARCHAR(10) DEFAULT NULL,PRIMARY KEY (a))"  \
       -h  127.0.0.1  -P ${port} -D test -p ${passwd}  \
       -n ${count}  \
       -c 100 -b 100
