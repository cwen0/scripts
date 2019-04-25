for i in `cat master`;do ssh $i 'yum install -y moosefs-master moosefs-cgi moosefs-cgiserv moosefs-cli;
echo "MFSMASTER_ENABLE=true" >> /etc/default/moosefs-master;
service moosefs-master restart;
echo "MFSCGISERV_ENABLE=true" >> /etc/default/moosefs-cgiserv;
service moosefs-cgiserv restart';done
