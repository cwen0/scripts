#!/bin/bash
# vim: filetype=sh

# Global variables
sn=tmux

# Functions
usage () {
    local pname=$(basename $0)
    cat <<EOS
    NAME
      $pname - ssh to multiple hosts with tmux.
    SYNOPSYS
      $pname open file
      $pname exec 'command'
      $pname password
      $pname close
    DESCRIPTION
      $ cat host.list
      host1
      host2
      host3
      $ $pname open host.list
        ssh to host1 host2 host3 in separate tmux window.
      $ $pname exec 'command'
        execute command on each hosts.
      $ $pname password
        send password to each hosts.
      $ $pname close
        close opened windows.
EOS
    exit 1
}

## open a file that contains a host name per line and then ssh to them.
do_open () {
    local f=$1
    local cnt=1

    tmux new-session -s "$sn" -n main -d

    while read host
    do
        tmux new-window -t "$sn:$cnt" -n ''
        tmux send-keys -t "$sn:$cnt" "ssh $host" C-m
        cnt=$(( $cnt + 1 ))
        $SLEEP $SLEEP_ARG
    done < "$f"

    # attach to main (number 0) window.
    tmux select-window -t "$sn:0"
    tmux -2 attach-session -t "$sn"
}

do_exec () {
    local window
    for window in `tmux list-windows -F '#{window_index}' | grep -v '0'`;
    do
        tmux send-keys -t "$sn:$window" "$@" C-m
    done
}

do_close () {
    tmux kill-session -t "$sn"
}

# set echo back considering Ctrl-C while "stty -echo".
trap "stty echo; exit 100" 2

do_password () {
    local pwd
    printf "Password:"
    stty -echo
    read pwd
    for window in `tmux list-windows -F '#{window_index}' | grep -v '0'`;
    do
        tmux send-keys -t "$sn:$window" "$pwd" C-m
    done
    stty echo
}

exit_with_msg () {
    local msg="$1"
    local status="$2"
    echo "ERROR: $msg"
    exit "$status"
}

prepare () {
    # OS specific settings.
    local os=`uname`
    case "$os" in
        "Darwin" )
            SLEEP="sleep"
            SLEEP_ARG=0.2 # 200 [msec]
            ;;
        "Linux" )
            SLEEP="usleep"
            SLEEP_ARG=200000 # 200 [msec]
            ;;
        *)
            exit_with_msg "OS <$os> is not supported." 10
            ;;
    esac
}

main () {
    prepare

    local command=$1

    case "$command" in
        "open" )
            local file=$2
            [ ! -f "$file" ] && usage
            do_open "$file"
            ;;
        "exec" )
            local command=$2
            [ "X$command" = "X" ] && usage
            do_exec "$command"
            ;;
        "close" )
            do_close
            ;;
        "password" )
            do_password
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"

exit $?
