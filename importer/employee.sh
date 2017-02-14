#!/bin/bash
if  [ $# != 3 ];  then
    echo "Usage: $0 port passwd  count"
    exit 1
fi

port=$1
passwd=$2
count=$3

importer -t "create table employee(Id int, Name varchar(20),Salary bigint,DepartmentID int);"  \
       -h  127.0.0.1  -P ${port} -D test -p ${passwd}  \
       -n ${count}  \
       -c 100 -b 100
