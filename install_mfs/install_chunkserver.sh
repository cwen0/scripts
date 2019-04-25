for i in `cat chunkserver`;do ssh $i '
yum install -y moosefs-chunkserver;
echo "MFSCHUNKSERVER_ENABLE=true" > /etc/default/moosefs-chunkserver;
mkdir -p /data/chunkserver;
chown -R mfs:mfs /data/chunkserver;
echo "/data/chunkserver" >> /etc/mfs/mfshdd.cfg';done

for i in `cat chunkserver`;do ssh $i "echo \"BIND_HOST = $i\" >> /etc/mfs/mfschunkserver.cfg; service moosefs-chunkserver restart"; done
