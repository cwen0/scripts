#!/bin/bash

perf record -F 99 -p $1 -g -- sleep 60
perf script > out.perf
./FlameGraph/stackcollapse-perf.pl out.perf > out.folded
./FlameGraph/flamegraph.pl out.folded > kernel.svg
curl --upload-file ./kernel.svg https://transfer.sh/kernel.svg

