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
                     "--read-lock=update --use-index-false"],
        "set-cas": ["", "--read-lock=update"],
        "set": [],
        # "sequential": [],
        "table":[]
    }


def gen_tests():
    nemesis = all_nemesis()
    workloads = workload_options()

    tests = []
    for w in workloads:
        for option in workloads[w]:
            for ne in nemesis:
                tests.append("lein run test --workload=" + w + " --time-limit=120 --concurrency 2n " +
                             "--nemesis=" + ne + " " + option + " --ssh-private-key /root/.ssh/id_rsa")

    return tests


def sampling(selection, offset=0, limit=None):
    return selection[offset:(limit + offset if limit is not None else None)]


def run_tests(offset, limit):
    tests = gen_tests()
    to_run_tests = sampling(tests, offset, limit)
    # print to_run_tests
    for test in to_run_tests:
        cmd = ["sh", "-c", "docker exec jepsen-control bash -c " +
                           "'cd /jepsen/tidb/ && timeout --preserve-status 7200 " + test + "> jepsen.log'"]

        print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE)

        if result.returncode != 0:
            print(result.stderr)
            print(result.stdout)
            sys.exit(1)


# def update_stores():



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--return-count", type=bool, default=False, help="return the numbers of test")
    parser.add_argument("--offset", type=int, default=0, help="offset of tests to run")
    parser.add_argument("--limit", type=int, default=5, help="limit of tests to run")

    args = parser.parse_args()

    if args.return_count:
        print (len(gen_tests()))
        sys.exit(0)

    run_tests(args.offset, args.limit)


if __name__ == "__main__":
    main()