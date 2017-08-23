#!/bin/bash
if  [ $# != 2 ];  then
    echo "Usage: $0 port count"
    exit 1
fi

port=$1
count=$2

importer -t "create table account(accno varchar(16) not null, accstate char(1) default '1' not null, realtimeremain decimal(18,2), currency char(3) not null, rate decimal(13,5) not null default 1, accnature char(1) default '1' not null, cuno varchar(15) not null, reserve1 varchar(500), reserve2 varchar(500), reserve3 varchar(500), reserve4 varchar(500) , primary key(accno), key account_idx1 (cuno))"  \
       -h  127.0.0.1  -P ${port} -D test \
       -n ${count}  \
       -c 100 -b 100
