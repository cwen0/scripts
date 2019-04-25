#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import argparse
import subprocess
import sys
import re
import json


def run_sysbench(bench, starttime, benchtime, warmuptime, count):
    results = []
    for index in range(count):
        restore_cluster()
        drop_cache()
        cmd = ["sh", "-c", "sysbench " + bench +
               " --mysql-host=127.0.0.1 --mysql-port=4000 --mysql-user=root" +
               " --mysql-db=sbtest" +
               " --time=" + str(benchtime) +
               " --report-interval=10 --db-driver=mysql --tables=32" +
               "--table-size=1000000 --threads=256 --warmup-time=" +
               str(warmuptime) +" run > "+ bench + str(index+1) + ".result"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(result.stderr)
            print(result.stdout)
            sys.exit(1)

        results = append(gen_sysbench_result(bench, index+1))

    data = {
        "bench_type": "sysbench",
        "bench_method": bench,
        "bench_time": starttime,
        "cluster_info": {
            "pd": get_pd_info(),
            "tidb": get_tidb_info(),
            "tikv": get_tikv_info()
        },
        "bench_result": {
            "tps": sum(d['tps'] for d in results) / len(results),
            "qps": sum(d['qps'] for d in results) / len(results),
            "lantency_avg": sum(d['lan_avg'] for in results) / len(results),
            "lantency_95th": sum(d['lan_95th'] for in results) / len(results),
            "time_elapsed": benchtime
        }
    }

    with open(bench+'.json', 'w') as outfile:
        json.dump(data, outfile)


def restore_cluster():
    cmd = ["sh", "-c", "ansible-playbook stop.yml;" +
           "ansible -i inventory.ini tikv_servers -m shell -a 'cd /tmp/tidb/deploy/; rm -rf data; cp -R data.bak data';" +
           "ansible -i inventory.ini pd_servers -m shell -a 'cd /tmp/tidb/deploy/; rm -rf data.pd; cp -R datapd.bak data.pd;'" +
                "ansible-playbook start.yml;'"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if result.returncode != 0:
        print(tps_result.stdout)
        print(result.stderr)
        sys.exit(1)


def drop_cache():
    cmd = ["sudo", "sh", "-c", "sync; /usr/bin/echo 3 > /proc/sys/vm/drop_caches"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if result.returncode != 0:
        print(tps_result.stdout)
        print(result.stderr)
        sys.exit(1)


def gen_sysbench_result(bench, index):
    tps_cmd = ["sh", "-c", "cat " + bench + str(index) + ".result |grep -e 'transactions:'|awk -F['(',' ']+ '{print $4}'"]
    tps_result = subprocess.run(tps_cmd, stdout=subprocess.PIPE)
    if tps_result.returncode != 0:
        print(tps_result.stdout)
        print(tps_result.stderr)
        sys.exit(1)

    qps_cmd = ["sh", "-c", "cat " + bench + str(index) + ".result |grep -e 'queries:'|awk -F['(',' ']+ '{print $4}'"]
    qps_result = subprocess.run(tps_cmd, stdout=subprocess.PIPE)
    if qps_result.returncode != 0:
        print(qps_result.stdout)
        print(qps_result.stderr)
        sys.exit(1)

    lan_avg_cmd = ["sh", "-c", "cat " + bench + str(index) + ".result | grep 'avg:' | awk '{print $2}'"]
    lan_avg_result = subprocess.run(lan_avg_cmd, stdout=subprocess.PIPE)
    if lan_avg_result.returncode != 0:
        print(lan_avg_result.stdout)
        print(lan_avg_result.stderr)
        sys.exit(1)

    lan_95th_cmd = ["sh", "-c", "cat " + bench + str(index) + ".result | grep '95th percentile:' | awk '{print $3}'"]
    lan_95th_result = subprocess.run(lan_95th_cmd, stdout=subprocess.PIPE)
    if lan_95th_result.returncode != 0:
        print(lan_95th_result.stdout)
        print(lan_95th_result.stderr)
        sys.exit(1)

    return {"tps": float(tps_result.stdout), "qps": float(qps_result.stdout),
            "lan_avg": float(lan_avg_result.stdout),
            "lan_95th": float(lan_95th_result.stdout)}


def get_pd_info():
    info = dict()
    cmd = ["sh", "-c", "./resources/bin/pd-server -V"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return info

    pattern = re.compile('Git Commit Hash: (.*?)\n')
    info["commit"] = re.findall(pattern, result.stdout.decode('utf-8'))[0]

    branch_pattern = re.compile("Git Branch: (.*?)\n")
    info["branch"] = re.findall(branch_pattern, result.stdout.decode('utf-8'))[0]

    tag_pattern = re.compile("Release Version: (.*?)\n")
    info["tag"] = re.findall(tag_pattern, result.stdout.decode('utf-8'))[0]
    info["count"] = 1
    return info


def get_tidb_info():
    info = dict()
    cmd = ["sh", "-c", "./resources/bin/tidb-server -V"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return info

    pattern = re.compile('Git Commit Hash: (.*?)\n')
    info["commit"] = re.findall(pattern, result.stdout.decode('utf-8'))[0]

    branch_pattern = re.compile("Git Branch: (.*?)\n")
    info["branch"] = re.findall(branch_pattern, result.stdout.decode('utf-8'))[0]

    tag_pattern = re.compile("Release Version: (.*?)\n")
    info["tag"] = re.findall(tag_pattern, result.stdout.decode('utf-8'))[0]
    info["count"] = 1
    return info


def get_tikv_info():
    info = dict()
    cmd = ["sh", "-c", "./resources/bin/tikv-server --version"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return info

    pattern = re.compile('Git Commit Hash: (.*?)\n')
    info["commit"] = re.findall(pattern, result.stdout.decode('utf-8'))[0]

    branch_pattern = re.compile("Git Commit Branch: (.*?)\n")
    info["branch"] = re.findall(branch_pattern, result.stdout.decode('utf-8'))[0]

    tag_pattern = re.compile("Release Version: (.*?)\n")
    info["tag"] = re.findall(tag_pattern, result.stdout.decode('utf-8'))[0]
    info["count"] = 1
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bench", type=str, required=True,
                        help="bench method, oltp_point_select/oltp_insert/oltp_update_index/oltp_update_non_index/oltp_read_write")
    parser.add_argument("-starttime", type=str, help="start time")
    parser.add_argument("-benchtime", type=int, help="bench time", default=3600)
    parser.add_argument("-warmuptime", type=int, help="warmup time", default=600)
    parser.add_argument("-count", type=int, help="run count", default=1)

    args = parser.parse_args()

    run_sysbench(args.bench, args.starttime, args.benchtime, args.warmuptime, args.count)


if __name__ == "__main__":
    main()
