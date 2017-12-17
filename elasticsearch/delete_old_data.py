#!/usr/bin/python
import argparse
from elasticsearch import Elasticsearch 

def deleteOldIndexes(host, port): 
    es = Elasticsearch([{'host': hostm, 'port': port}])
    del_date = int((datetime.datetime.today() + datetime.timedelta(-7)).strftime("%Y%m%d"))

    res = es.cat.indices(index="logstash-*")

    for index in res.split('\n'):
        if index != '':
            print index
            index_name = index.split(' ')[2]
            print index_name
            index_date = int(('').join(index.split(' ')[2].split('-')[2].split('.')))
            if index_date < del_date:
                print index_date
                es.indices.delete(index='logstash-%s' %index_name,
                              request_timeout=300)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="host for the elasticsearch instance")
    parser.add_argument("port", help="port for the elasticsearch instance")

    args = parser.parse_args()

    deleteOldIndexes(args.host, args.port)


if __name__ == "__main__":
    main()
