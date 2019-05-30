#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import argparse
import subprocess
import sys
import re
import json
import numpy as np


def run_sysbench(bench_method, randtype, starttime, benchtime, warmuptime, count, threads):
    results = []
    for index in range(count):
        restore_cluster()
        drop_cache()
        cmd = ["sh", "-c", "sysbench " + bench_method +
               " --mysql-host=127.0.0.1 --mysql-port=4000 --mysql-user=root" +
               " --mysql-db=sbtest" +
               " --time=" + str(benchtime) +
               " --rand-type=" + randtype +
               " --mysql-ignore-errors=all" +
               " --report-interval=10 --db-driver=mysql --tables=32" +
               " --threads=" + threads +
               " --table-size=1000000 --warmup-time=" +
               str(warmuptime) + " run > " + "{}_{}".format(bench_method, randtype) + str(index+1) + ".result"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(result.stderr)
            print(result.stdout)
            sys.exit(1)

        one_result = gen_sysbench_result("{}_{}".format(bench_method, randtype), index+1)
        print(one_result)
        results.append(one_result)

    handle_data(bench_method, randtype, starttime, benchtime, results)


def handle_data(bench_method, randtype, starttime, benchtime, values):
    tps_list = []
    tps_list.extend(d["tps"] for d in values)
    tps_dict = computeStats(tps_list)

    qps_list = []
    qps_list.extend(d["qps"] for d in values)
    qps_dict = computeStats(qps_list)

    lantency_avg_list = []
    lantency_avg_list.extend(d["lan_avg"] for d in values)
    lantency_avg_dict = computeStats(lantency_avg_list)

    lantency_95th_list = []
    lantency_95th_list.extend(d["lan_95th"] for d in values)
    lantency_95th_dict = computeStats(lantency_95th_list)

    data = {
        "bench_type": "sysbench" if randtype == "special" or randtype == "" else "sysbench_{}".format(randtype),
        "bench_method": bench_method,
        "bench_time": starttime,
        "cluster_info": {
            "pd": get_pd_info(),
            "tidb": get_tidb_info(),
            "tikv": get_tikv_info()
        },
        "bench_result": {
            "tps_value": tps_dict["value"],
            "tps_deviation": tps_dict["deviation"],
            "tps_var": tps_dict["var"],
            "tps_std": tps_dict["std"],
            "qps_value": qps_dict["value"],
            "qps_deviation": qps_dict["deviation"],
            "qps_var": qps_dict["var"],
            "qps_std": qps_dict["std"],
            "lantency_avg_value": lantency_avg_dict["value"],
            "lantency_avg_deviation": lantency_avg_dict["deviation"],
            "lantency_avg_var": lantency_avg_dict["var"],
            "lantency_avg_std": lantency_avg_dict["std"],
            "lantency_95th_value": lantency_95th_dict["value"],
            "lantency_95th_deviation": lantency_95th_dict["deviation"],
            "lantency_95th_var": lantency_95th_dict["var"],
            "lantency_95th_std": lantency_95th_dict["std"],
            "time_elapsed": benchtime
        }
    }

    print(data)

    with open(bench_method+'.json', 'w') as outfile:
        json.dump(data, outfile)


def computeStats(values):
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    lo = q1 - 1.5 * (q3 - q1)
    hi = q3 + 1.5 * (q3 - q1)

    r_values = []

    for v in values:
        if lo <= v and v <= hi:
            r_values.append(v)

    data = {
        "min": np.min(r_values),
        "max": np.max(r_values),
        "mean": round(np.mean(r_values), 3),
        "var": round(np.var(r_values), 4),
        "std": round(np.std(r_values), 4)
    }

    data["deviation"] = round(deviation(data), 5)
    data["value"] = data["mean"]

    return data


def deviation(data):
    if data["mean"] == 0 or data["max"] == 0:
        return 0

    diff = 1 - data["min"]/data["mean"]
    d = data["max"] / data["mean"] - 1
    if d > diff:
        diff = d

    # return "± %.2f%%" % (diff * 100)
    return diff


def restore_cluster():
    cmd = ["bash", "./restore.sh", "> restore.log"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if result.returncode != 0:
        result_2 = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result_2.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            sys.exit(1)


def drop_cache():
    cmd = ["sudo", "sh", "-c",
           "sync; /usr/bin/echo 3 > /proc/sys/vm/drop_caches"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)


def gen_sysbench_result(bench, index):
    tps_cmd = ["sh", "-c", "cat " + bench + str(index) +
               ".result |grep -e 'transactions:'|awk -F['(',' ']+ '{print $4}'"]
    tps_result = subprocess.run(tps_cmd, stdout=subprocess.PIPE)
    if tps_result.returncode != 0:
        print(tps_result.stdout)
        print(tps_result.stderr)
        sys.exit(1)

    qps_cmd = ["sh", "-c", "cat " + bench + str(index) +
               ".result |grep -e 'queries:'|awk -F['(',' ']+ '{print $4}'"]
    qps_result = subprocess.run(qps_cmd, stdout=subprocess.PIPE)
    if qps_result.returncode != 0:
        print(qps_result.stdout)
        print(qps_result.stderr)
        sys.exit(1)

    lan_avg_cmd = ["sh", "-c", "cat " + bench + str(index) +
                   ".result | grep 'avg:' | awk '{print $2}'"]
    lan_avg_result = subprocess.run(lan_avg_cmd, stdout=subprocess.PIPE)
    if lan_avg_result.returncode != 0:
        print(lan_avg_result.stdout)
        print(lan_avg_result.stderr)
        sys.exit(1)

    lan_95th_cmd = ["sh", "-c", "cat " + bench + str(index) +
                    ".result | grep '95th percentile:' | awk '{print $3}'"]
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
    info["commit"] = re.findall(pattern,
                                result.stdout.decode('utf-8'))[0].strip()

    branch_pattern = re.compile("Git Branch: (.*?)\n")
    info["branch"] = re.findall(branch_pattern,
                                result.stdout.decode('utf-8'))[0].strip()

    tag_pattern = re.compile("Release Version: (.*?)\n")
    info["tag"] = re.findall(tag_pattern,
                             result.stdout.decode('utf-8'))[0].strip()

    build_time = re.compile("UTC Build Time: (.*?)\n")
    info["build_time"] = re.findall(build_time,
                                    result.stdout.decode('utf-8'))[0].strip()

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
    info["commit"] = re.findall(pattern,
                                result.stdout.decode('utf-8'))[0].strip()

    branch_pattern = re.compile("Git Branch: (.*?)\n")
    info["branch"] = re.findall(branch_pattern,
                                result.stdout.decode('utf-8'))[0].strip()

    tag_pattern = re.compile("Release Version: (.*?)\n")
    info["tag"] = re.findall(tag_pattern,
                             result.stdout.decode('utf-8'))[0].strip()

    build_time = re.compile("UTC Build Time: (.*?)\n")
    info["build_time"] = re.findall(build_time,
                                    result.stdout.decode('utf-8'))[0].strip()

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
    info["commit"] = re.findall(pattern,
                                result.stdout.decode('utf-8'))[0].strip()

    branch_pattern = re.compile("Git Commit Branch: (.*?)\n")
    info["branch"] = re.findall(branch_pattern,
                                result.stdout.decode('utf-8'))[0].strip()

    tag_pattern = re.compile("Release Version: (.*?)\n")
    info["tag"] = re.findall(tag_pattern,
                             result.stdout.decode('utf-8'))[0].strip()

    build_time = re.compile("UTC Build Time: (.*?)\n")
    info["build_time"] = re.findall(build_time,
                                    result.stdout.decode('utf-8'))[0].strip()

    info["count"] = 1
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bench", type=str, required=True,
                        help="bench method, oltp_point_select/oltp_insert/oltp_update_index/oltp_update_non_index/oltp_read_write")
    parser.add_argument("-starttime", type=str, help="start time")
    parser.add_argument("-benchtime", type=int,
                        help="bench time", default=3600)
    parser.add_argument("-warmuptime", type=int,
                        help="warmup time", default=600)
    parser.add_argument("-count", type=int, help="run count", default=1)
    parser.add_argument("-randtype", type=str, help="random numbers distribution", default="special")
    parser.add_argument("-threads", type=int, help="threads count", default=256)

    args = parser.parse_args()

    run_sysbench(args.bench, args.randtype, args.starttime,
                 args.benchtime, args.warmuptime, args.count, args.threads)


if __name__ == "__main__":
    main()
