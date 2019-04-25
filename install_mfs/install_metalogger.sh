for i in `cat metalogger`;do ssh $i '
yum install -y moosefs-metalogger;
echo "MFSMETALOGGER_ENABLE=true" > /etc/default/moosefs-metalogger;
service moosefs-metalogger start'; done

