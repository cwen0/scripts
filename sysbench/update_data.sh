#! /bin/bash
## yum install -y epel-release
## yum install -y jq bc
## all bench results store at the data sub dir

report=""
case="0"
buffer=""

for datafile in $(ls -L data/); do
    data=$(cat data/$datafile)
    bench_type=$(echo $data  | jq '.bench_type' | grep -Eo '[^"]+')
    bench_method=$(echo $data  | jq '.bench_method' | grep -Eo '[^"]+')
    bench_time=$(echo $data  | jq '.bench_time' | grep -Eo '[^"]+')

    pd_commit=$(echo $data  | jq '.cluster_info.pd.commit' | grep -Eo '[^"]+')
    pd_branch=$(echo $data  | jq '.cluster_info.pd.branch' | grep -Eo '[^"]+')
    pd_tag=$(echo $data  | jq '.cluster_info.pd.tag' | grep -Eo '[^"]+')
    pd_count=$(echo $data  | jq '.cluster_info.pd.count' | grep -Eo '[^"]+')
    pd_build_time=$(echo $data  | jq '.cluster_info.pd.build_time' | grep -Eo '[^"]+')

    tidb_commit=$(echo $data  | jq '.cluster_info.tidb.commit' | grep -Eo '[^"]+')
    tidb_branch=$(echo $data  | jq '.cluster_info.tidb.branch' | grep -Eo '[^"]+')
    tidb_tag=$(echo $data  | jq '.cluster_info.tidb.tag' | grep -Eo '[^"]+')
    tidb_count=$(echo $data  | jq '.cluster_info.tidb.count' | grep -Eo '[^"]+')
    tidb_build_time=$(echo $data  | jq '.cluster_info.tidb.build_time' | grep -Eo '[^"]+')

    tikv_commit=$(echo $data  | jq '.cluster_info.tikv.commit' | grep -Eo '[^"]+')
    tikv_branch=$(echo $data  | jq '.cluster_info.tikv.branch' | grep -Eo '[^"]+')
    tikv_tag=$(echo $data  | jq '.cluster_info.tikv.tag' | grep -Eo '[^"]+')
    tikv_count=$(echo $data  | jq '.cluster_info.tikv.count' | grep -Eo '[^"]+')
    tikv_build_time=$(echo $data  | jq '.cluster_info.tikv.build_time' | grep -Eo '[^"]+')

    tps=$(echo $data | jq '.bench_result.tps_value' | grep -Eo '[^"]+')
    tps_deviation=$(echo $data | jq '.bench_result.tps_deviation' | grep -Eo '[^"]+')
    tps_std=$(echo $data | jq '.bench_result.tps_std' | grep -Eo '[^"]+')

    qps=$(echo $data | jq '.bench_result.qps_value' | grep -Eo '[^"]+')
    qps_deviation=$(echo $data | jq '.bench_result.qps_deviation' | grep -Eo '[^"]+')
    qps_std=$(echo $data | jq '.bench_result.qps_std' | grep -Eo '[^"]+')

    lantency_avg=$(echo $data | jq '.bench_result.lantency_avg_value' | grep -Eo '[^"]+')
    lantency_avg_deviation=$(echo $data | jq '.bench_result.lantency_avg_deviation' | grep -Eo '[^"]+')
    lantency_avg_std=$(echo $data | jq '.bench_result.lantency_avg_std' | grep -Eo '[^"]+')

    lantency_95th=$(echo $data | jq '.bench_result.lantency_95th_value' | grep -Eo '[^"]+')
    lantency_95th_deviation=$(echo $data | jq '.bench_result.lantency_95th_deviation' | grep -Eo '[^"]+')
    lantency_95th_std=$(echo $data | jq '.bench_result.lantency_95th_std' | grep -Eo '[^"]+')

    time_elapsed=$(echo $data | jq '.bench_result.time_elapsed' | grep -Eo '[^"]+')

    last_tps=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="tps"}' | jq '.data.result[0].value[1]' | grep -Eo '[^"]+')
    last_qps=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="qps"}' | jq '.data.result[0].value[1]' | grep -Eo '[^"]+')
    # last_qps_deviation=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="metadata"}' | jq '.data.result[0].metric.qps_deviation' | grep -Eo '[^"]+')

    last_lantency_avg=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="lantency_avg"}' | jq '.data.result[0].value[1]' | grep -Eo '[^"]+')
    # last_lantency_avg_deviation=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="metadata"}' | jq '.data.result[0].metric.lantency_avg_deviation' | grep -Eo '[^"]+')

    last_lantency_95th=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="lantency_95th"}' | jq '.data.result[0].value[1]' | grep -Eo '[^"]+')
    # last_lantency_95th_deviation=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="metadata"}' | jq '.data.result[0].metric.lantency_95th_deviation' | grep -Eo '[^"]+')

    last_tidb=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="tps"}' | jq '.data.result[0].metric.tidb' | grep -Eo '[^"]+')
    last_tikv=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="tps"}' | jq '.data.result[0].metric.tikv' | grep -Eo '[^"]+')
    last_pd=$(curl -s 'http://172.16.30.14:9090/api/v1/query' --data-urlencode 'query=benchmark{bench_type="'$bench_type'",bench_method="'$bench_method'",tidb_branch="'$tidb_branch'",indicator="tps"}' | jq '.data.result[0].metric.pd' | grep -Eo '[^"]+')

    [[ $last_tps == "null" || -z $last_tps ]] && last_tps=$tps
    [[ $last_qps == "null" || -z $last_qps ]] && last_qps=$qps
    [[ $last_lantency_avg == "null" || -z $last_lantency_avg ]] && last_lantency_avg=$lantency_avg
    [[ $last_lantency_95th == "null" || -z $last_lantency_95th ]] && last_lantency_95th=$lantency_95th

    buffer="$buffer
benchmark{bench_type=\"$bench_type\",bench_method=\"$bench_method\",tidb_branch=\"$tidb_branch\",indicator=\"tps\",pd=\"$pd_commit($pd_branch) $pd_build_time\",tidb=\"$tidb_commit($tidb_branch) $tidb_build_time\",tikv=\"$tikv_commit($tikv_branch) $tikv_build_time\"} $tps
benchmark{bench_type=\"$bench_type\",bench_method=\"$bench_method\",tidb_branch=\"$tidb_branch\",indicator=\"qps\"} $qps
benchmark{bench_type=\"$bench_type\",bench_method=\"$bench_method\",tidb_branch=\"$tidb_branch\",indicator=\"lantency_avg\"} $lantency_avg
benchmark{bench_type=\"$bench_type\",bench_method=\"$bench_method\",tidb_branch=\"$tidb_branch\",indicator=\"lantency_95th\"} $lantency_95th"
# benchmark{bench_type=\"$bench_type\",bench_method=\"$bench_method\",tidb_branch=\"$tidb_branch\",indicator=\"metadata\",tps_deviation=\"$tps_deviation\",tps_std=\"$tps_std\",qps_deviation=\"$qps_deviation\",qps_std=\"$qps_std\",lantency_avg_deviation=\"$lantency_avg_deviation\",lantency_avg_std=\"$lantency_avg_std\",lantency_95th_deviation=\"$lantency_95th_deviation\",lantency_95th_std=\"$lantency_95th_std\"} 1"

    if [[ -z $report ]]; then
        report="Version:
tidb: $tidb_commit($tidb_branch) $tidb_build_time
tikv: $tikv_commit($tikv_branch) $tikv_build_time
pd: $pd_commit($pd_branch) $pd_build_time

Pre version:
tidb: $last_tidb
tikv: $last_tikv
pd: $last_pd

Create Time: $bench_time"
    fi
    report="$report

test-$case: < $bench_method >
    * QPS : $qps ± $(echo "$qps_deviation * 100" | bc | awk '{printf "%.2f\n", $0}')% (std=$qps_std) delta: $(echo 'scale=2; ('$qps' - '$last_qps') * 100 / '$last_qps | bc | awk '{printf "%.2f\n", $0}')% 
    * AvgMs : $lantency_avg ± $(echo "$lantency_avg_deviation * 100" | bc | awk '{printf "%.2f\n", $0}')% (std=$lantency_avg_std) delta: $(echo 'scale=2; ('$lantency_avg' - '$last_lantency_avg') * 100 / '$lantency_avg | bc | awk '{printf "%.2f\n", $0}')%
    * PercentileMs95 : $lantency_95th ± $(echo "$lantency_95th_deviation * 100" | bc | awk '{printf "%.2f\n", $0}')% (std=$lantency_95th_std) delta: $(echo 'scale=2; ('$lantency_95th' - '$last_lantency_95th') * 100 / '$lantency_95th | bc | awk '{printf "%.2f\n", $0}')%"
    case=$((case+1))
done

echo "$buffer" | curl -s --data-binary @- http://172.16.30.14:9091/metrics/job/pushgateway

echo "$report

http://172.16.30.12:30000/d/Ta8TFPzWz/benchmark?orgId=1"
