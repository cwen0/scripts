#!/bin/bash
PORT=4000
HOST=127.0.0.1
COUNT=100000000

for ((i=0; i<10; i++ ));
do
    importer -t "create table table${i}(Id int, a varchar(20), b varchar(20), c varchar(20);"  \
        -h ${HOST}  -P ${PORT} -D test   \
        -n ${COUNT}  \
        -c 100 -b 100
done

