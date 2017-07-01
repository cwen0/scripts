set @@session.tidb_distsql_scan_concurrency=50; select count(*) from chepai_3k t group by t.city;
