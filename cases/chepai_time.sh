echo case1:
for i in {1 2 5};
do
	echo ***${i}kw***
	time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "set @@session.tidb_distsql_scan_concurrency=50; select count(*) from chepai_${i}k;" >/dev/null
    sleep 20
done

echo case2:
echo ***1kw join 1kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(s.id) FROM chepai_1k t join chepai_1k s on t.city = s.city group by s.nation;" >/dev/null
sleep 20
echo ***2kw join 1kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(s.id) FROM chepai_2k t join chepai_1k s on t.city = s.city group by s.nation;" >/dev/null
sleep 20
echo ***2kw join 2kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(s.id) FROM chepai_2k t join chepai_2k s on t.city = s.city group by s.nation;" >/dev/null
sleep 20
echo case3:
for i in {1 2 5};
do
        echo ***${i}kw***
        time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "set @@session.tidb_distsql_scan_concurrency=50; select count(*) from chepai_${i}k t group by t.city;" >/dev/null
        sleep 20
done

echo case4:
echo ***1kw + 1kw + 1kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(id) FROM (select * from chepai_1k t union all select * from chepai_1k s union all select * from chepai_1k k) s group by nation;" >/dev/null
sleep 20
echo ***2kw + 1kw + 5kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(id) FROM (select * from chepai_2k t union all select * from chepai_1k s union all select * from chepai_5k k) s group by nation;" >/dev/null
sleep 20
echo ***2kw + 2kw + 5kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(id) FROM (select * from chepai_2k t union all select * from chepai_2k s union all select * from chepai_5k k) s group by nation;" >/dev/null
sleep 20
echo ***2kw + 5kw + 5kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(id) FROM  (select * from chepai_2k t union all select * from chepai_5k s union all select * from chepai_5k k) s group by nation;" >/dev/null
sleep 20
echo ***5kw + 5kw + 5kw***
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "SELECT count(id) FROM  (select * from chepai_5k t union all select * from chepai_5k s union all select * from chepai_5k k) s group by nation;" >/dev/null
sleep 20

echo case5:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select * from chepai_1k t where 3 < (select count(id) from chepai_1k s where t.city = s.city);" >/dev/null
