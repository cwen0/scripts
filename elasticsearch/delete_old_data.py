#!/usr/bin/python
import argparse
import datetime
import pyelasticsearch
from elasticsearch import Elasticsearch 

def deleteOldIndexes(host, port): 
    es = Elasticsearch([{'host': host, 'port': port}])
    del_date = int((datetime.datetime.today() + datetime.timedelta(-7)).strftime("%Y%m%d"))

    indices = es.indices.get('_all')

    for index in indices:
        if index.find("logstash") != -1:
            index_date = int(('').join(index.split('-')[1].split('.')))
            if index_date < del_date:
		print 'delete :%s' %index
                es.indices.delete(index, request_timeout=300)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="host for the elasticsearch instance")
    parser.add_argument("port", help="port for the elasticsearch instance")

    args = parser.parse_args()

    deleteOldIndexes(args.host, args.port)


if __name__ == "__main__":
    main()
