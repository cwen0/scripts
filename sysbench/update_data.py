#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import json
import sys
import logging
import datetime
from influxdb import InfluxDBClient

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def handle_sysbench_file(path, name):
    result = dict()
    with open(path + "/" + name, "r") as outfile:
        result = json.load(outfile)

    client = InfluxDBClient('172.16.30.11', 8086, '', '', 'benchbot')
    old_result = client.query("""
                select * from benchbot
                where bench_method = '%s'
                order by time desc limit 1 """ % (result["bench_method"]))

    last_result = dict()
    if last_result is not None and len(list(old_result.get_points())) != 0:
        last_result = list(old_result.get_points())[0]

    if result["bench_time"] is None:
        result["bench_time"] = datetime.datetime.now()

    data = [{
        "measurement": "benchbot",
        "tags": {
            "bench_type": result["bench_type"],
            "bench_method": result["bench_method"],
            "tidb_commit": result["cluster_info"]["tidb"]["commit"],
            "tidb_branch": result["cluster_info"]["tidb"]["branch"],
            "tidb_build_time": result["cluster_info"]["tidb"]["build_time"],
            "tidb_tag": result["cluster_info"]["tidb"]["tag"],
            "pd_commit": result["cluster_info"]["pd"]["commit"],
            "pd_branch": result["cluster_info"]["pd"]["branch"],
            "pd_tag": result["cluster_info"]["pd"]["tag"],
            "pd_build_time": result["cluster_info"]["pd"]["build_time"],
            "tikv_commit": result["cluster_info"]["tikv"]["commit"],
            "tikv_branch": result["cluster_info"]["tikv"]["branch"],
            "tikv_tag": result["cluster_info"]["tikv"]["tag"],
            "tikv_build_time": result["cluster_info"]["tikv"]["build_time"]
        },
        "time": result.get("bench_time", datetime.datetime.now()),
        # "fields": result["bench_result"]}]
        "fields": {
            "tps_value": float(result.get("bench_result", {}).get("tps_value", 0)),
            "tps_deviation": float(result.get("bench_result", {}).get("tps_deviation", 0)),
            "tps_var": float(result.get("bench_result", {}).get("tps_var", 0)),
            "tps_std": float(result.get("bench_result", {}).get("tps_std", 0)),
            "qps_value": float(result.get("bench_result", {}).get("qps_value", 0)),
            "qps_deviation": float(result.get("bench_result", {}).get("qps_deviation", 0)),
            "qps_var": float(result.get("bench_result", {}).get("qps_var", 0)),
            "qps_std": float(result.get("bench_result", {}).get("qps_std", 0)),
            "lantency_avg_value": float(result.get("bench_result", {}).get("lantency_avg_value", 0)),
            "lantency_avg_deviation": float(result.get("bench_result", {}).get("lantency_avg_deviation", 0)),
            "lantency_avg_var": float(result.get("bench_result", {}).get("lantency_avg_var", 0)),
            "lantency_avg_std": float(result.get("bench_result", {}).get("lantency_avg_std", 0)),
            "lantency_95th_value": float(result.get("bench_result", {}).get("lantency_95th_value", 0)),
            "lantency_95th_deviation": float(result.get("bench_result", {}).get("lantency_95th_deviation", 0)),
            "lantency_95th_var": float(result.get("bench_result", {}).get("lantency_95th_var", 0)),
            "lantency_95th_std": float(result.get("bench_result", {}).get("lantency_95th_std", 0)),
            "time_elapsed": result.get("bench_result", {}).get("time_elapsed", 0)}}]

    try:
        client.write_points(data)
        # logging.info("writed %s to influxdb", result)
    except Exception as err:
        logging.error("write %s to influxdb", data)
        logging.traceback(err)
        sys.exit(1)

    return {
        "name": result["bench_method"],
        "current": result,
        "last_point": last_result
    }


def main():
    results = []
    files = os.listdir("data")
    for file in files:
        results.append(handle_sysbench_file("data", file))

    if len(results) <= 0:
        logging.error("results is empty")
        sys.exit(1)

    print("""Version:
tidb: %s(%s) %s
tikv: %s(%s) %s
pd: %s(%s) %s
    """ % (results[0].get("current", {}).get("cluster_info", {}).get("tidb", {}).get("commit", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("tidb", {}).get("branch", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("tidb", {}).get("build_time", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("tikv", {}).get("commit", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("tikv", {}).get("branch", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("tikv", {}).get("build_time", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("pd", {}).get("commit", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("pd", {}).get("branch", ""),
           results[0].get("current", {}).get("cluster_info", {}).get("pd", {}).get("build_time", "")))

    print("""Pre Version:
tidb: %s(%s) %s
tikv: %s(%s) %s
pd: %s(%s) %s
    """ % (results[0].get("last_point", {}).get("tidb_commit", ""),
           results[0].get("last_point", {}).get("tidb_branch", ""),
           results[0].get("last_point", {}).get("tidb_build_time", ""),
           results[0].get("last_point", {}).get("tikv_commit", ""),
           results[0].get("last_point", {}).get("tikv_branch", ""),
           results[0].get("last_point", {}).get("tikv_build_time", ""),
           results[0].get("last_point", {}).get("pd_commit", ""),
           results[0].get("last_point", {}).get("pd_branch", ""),
           results[0].get("last_point", {}).get("pd_build_time", "")))

    for index, value in enumerate(results):
        print("""test-%s: < %s >
    * QPS : %.2f ± %.4f%% (std=%.2f) delta: %.2f%%
    * AvgMs : %.2f ± %.4f%% (std=%.2f) delta: %.2f%%
    * PercentileMs95 : %.2f ± %.4f%% (std=%.2f) delta: %.2f%%
        """ % (index+1,
               value.get("name"), 
               value.get("current", {}).get("bench_result", {}).get("qps_value", 0),
               value.get("current", {}).get("bench_result", {}).get("qps_deviation", 0) * 100,
               value.get("current", {}).get("bench_result", {}).get("qps_std"),
               ((value.get("current", {}).get("bench_result", {}).get("qps_value", 0) -
                value.get("last_point", {}).get("qps_value", 0))/value.get("last_point", {}).get("qps_value", 1)) * 100,
               value.get("current", {}).get("bench_result", {}).get("lantency_avg_value", 0),
               value.get("current", {}).get("bench_result", {}).get("lantency_avg_deviation", 0) * 100,
               value.get("current", {}).get("bench_result", {}).get("lantency_avg_std"),
               ((value.get("current", {}).get("bench_result", {}).get("lantency_avg_value", 0) -
                value.get("last_point", {}).get("lantency_avg_value", 0))/value.get("last_point", {}).get("lantency_avg_value", 1)) * 100,
               value.get("current", {}).get("bench_result", {}).get("lantency_95th_value", 0),
               value.get("current", {}).get("bench_result", {}).get("lantency_95th_deviation", 0) * 100,
               value.get("current", {}).get("bench_result", {}).get("lantency_95th_std"),
               ((value.get("current", {}).get("bench_result", {}).get("lantency_95th_value", 0) -
                 value.get("last_point", {}).get("lantency_95th_value", 0))/value.get("last_point", {}).get("lantency_95th_value", 1)) * 100))

    print("http://172.16.30.12:30000/d/Ta8TFPzWz/benchmark?orgId=1")



if __name__ == "__main__":
    main()
