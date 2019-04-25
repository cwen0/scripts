for i in `cat all`;do ssh $i '
mkdir -p /data/coredump
chmod -R 777 /data/coredump
echo "/data/coredump/core.%e.%p" >/proc/sys/kernel/core_pattern
';done

