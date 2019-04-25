for i in `cat all`;do ssh $i '
yum install -y fuse;
yum install -y moosefs-client;
mkdir -p /mnt/mfs;
chmod -R 777 /mnt/mfs;
mfsmount /mnt/mfs -H mfsmaster';
done

