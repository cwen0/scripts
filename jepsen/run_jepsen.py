#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import subprocess


def all_nemesis():
    process_faults = ["kill-pd", "kill-kv", "kill-db", "pause-pd", "pause-kv", "pause-db"]
    network_faults = ["partition"]
    schedule_faults = ["shuffle-leader", "shuffle-region", "random-merge"]
    # clock_faults = "clock-skew"

    nemesis = ["none"]
    nemesis.extend(process_faults)
    nemesis.extend(network_faults)
    nemesis.extend(schedule_faults)
    # for n in schedule_faults:
    #     for pf in process_faults:
    #         nemesis.append(n+","+pf)
    #     for nf in network_faults:
    #         nemesis.append(n+","+nf)
    #nemesis.append("kill-pd,kill-db,pause-pd,kill-kv,shuffle-leader,partition,"
    #               "shuffle-region,pause-kv,pause-db,random-merge")

    return nemesis


def workload_options():
    return {
        "append": ["",
                   "--predicate-read=true",
                   "--read-lock=update --predicate-read=true",
                   "--read-lock=update --predicate-read=false"],
        # "bank": ["--update-in-place=true", "--update-in-place=false",
        #          "--read-lock=update --update-in-place=true",
        #          "--read-lock=update --update-in-place=false"],
        "bank-multitable": ["",
                            "--update-in-place=true",
                            "--read-lock=update --update-in-place=true",
                            "--read-lock=update --update-in-place=false"],
        # "long-fork": ["--use-index=true", "--use-index=false"],
        # "monotonic": ["--use-index=true", "--use-index=false"],
        "register": ["",
                     "--use-index=true",
                     "--read-lock=update --use-index=true",
                     "--read-lock=update --use-index=false"],
        "set-cas": ["", "--read-lock=update"],
        "set": [],
        # "sequential": [],
        "table": []
    }


def workload_options_only_for_update():
    return {
        "bank": ["--read-lock=update"],
        "bank-multitable": ["--read-lock=update --update-in-place=true",
                            "--read-lock=update --update-in-place=false"],
        "register": ["--read-lock=update --use-index=true",
                     "--read-lock=update --use-index=false"],
        "set-cas": ["--read-lock=update"]
    }


def gen_tests(version, tarball, time_limit, only_for_update):
    nemesis = all_nemesis()

    workloads = workload_options()

    if only_for_update:
        workloads = workload_options_only_for_update()

    tests = []
    for w in workloads:
        for option in workloads[w]:
            for ne in nemesis:
                tests.append("lein run test --workload=" + w + " --time-limit=" + str(time_limit) + " --concurrency 2n" +
                             " --auto-retry=default --auto-retry-limit=default" +
                             " --version=" + version + " --tarball-url=" + tarball +
                             " --nemesis=" + ne + " " + option + " --ssh-private-key /root/.ssh/id_rsa")

    tests.sort()
    return  tests


def sampling(selection, offset=0, limit=None):
    return selection[offset:(limit + offset if limit is not None else None)]


def run_tests(offset, limit, unique_id, file_server, version, tarball, time_limit, only_for_update):
    tests = gen_tests(version, tarball, time_limit, only_for_update)
    to_run_tests = sampling(tests, offset, limit)
    # print to_run_tests
    for test in to_run_tests:
        cmd = ["sh", "-c", "docker exec jepsen-control bash -c " +
                           "'cd /jepsen/tidb/ && timeout --preserve-status 7200 " + test + "> jepsen.log'"]

        max_retry = 3
        for i in range(max_retry):
            print(cmd)
            result = subprocess.run(cmd, stdout=subprocess.PIPE)

            if result.returncode != 0:
                print(result.stderr)
                print(result.stdout)

                if i >= max_retry-1:
                    print("failed to exec jepsen test")
                    update_stores(offset, limit, unique_id, file_server)
                    sys.exit(1)

                print("retry...")
            else:
                break


    update_stores(offset, limit, unique_id, file_server)


def update_stores(offset, limit, unique_id, file_server):
    end = offset+limit
    store_name = "store-" + str(offset) + "-" + str(end) + ".tar.gz"
    filepath = "tests/pingcap/jepsen/" + str(unique_id) + "/" + store_name
    cmd = ["sh", "-c", "docker exec jepsen-control bash -c " +
           "'cd /jepsen/tidb/ && tar -zcvf " + store_name + " store && " +
           " curl -F " + filepath + "=@" + store_name + " " + file_server + "/upload'"]
    print(cmd)
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if result.returncode != 0:
        print(result.stderr)
        print(result.stdout)
        sys.exit(1)

    print(file_server + "/download/tests/pingcap/jepsen/" + str(unique_id) + "/" + store_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--return-count", type=bool, default=False, help="return the numbers of test")
    parser.add_argument("--offset", type=int, default=0, help="offset of tests to run")
    parser.add_argument("--limit", type=int, default=5, help="limit of tests to run")
    parser.add_argument("--unique-id", type=int, default=0, help="unique id")
    parser.add_argument("--file-server", type=str, default="http://fileserver.pingcap.net", help="file server")
    parser.add_argument("--version", type=str, default="latest", help="tidb version")
    parser.add_argument("--tarball", type=str,
                        default="http://172.16.30.25/download/builds/pingcap/release/tidb-latest-linux-amd64.tar.gz",
                        help="tidb tarball url")
    parser.add_argument("--time-limit", type=int, default=120, help="time limit for each jepsen test")
    parser.add_argument("--only-for-update", type=bool, default=False, help="only run test case with `select for update`")

    args = parser.parse_args()

    if args.return_count:
        print (len(gen_tests(args.version, args.tarball, args.time_limit, args.only_for_update)))
        sys.exit(0)

    run_tests(args.offset, args.limit, args.unique_id, args.file_server, args.version, args.tarball, args.time_limit, args.only_for_update)


if __name__ == "__main__":
    main()
