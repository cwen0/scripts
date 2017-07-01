echo case1:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select count(*) from t;" >/dev/null
echo case2:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select * from orders where exists (select * from customer where orders.o_custkey = customer.c_custkey);" >/dev/null
echo case3:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select sum(orders.o_totalprice) from orders left join customer on orders.o_custkey = customer.c_custkey;" >/dev/null
echo case4:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select 100.00 * sum(case when p_type like 'PROMO%'  then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue from lineitem, part where l_partkey = p_partkey;" >/dev/null
echo case5:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select o_orderpriority, count(*) as order_count from orders where exists (select * from lineitem where l_orderkey = o_orderkey and l_commitdate < l_receiptdate  )group by o_orderpriority order by o_orderpriority;" >/dev/null
echo case6:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select d.Name, e.Name, e.Salary from department d, employee e where e.DepartmentId = d.Id and 3 > (select count(distinct Salary) from employee where e.Salary < employee.Salary and e.DepartmentId = employee.DepartmentId) order by e.Salary desc;" >/dev/null
echo case7:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select d.Name, e.Name as Employee , e.Salary from employee e join (select max(Salary) as Salary ,DepartmentId from employee group by DepartmentId) h on h.DepartmentId = e.DepartmentId and e.Salary = h.Salary  join  department d on d.Id = e.DepartmentId;" >/dev/null
echo case8:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select * from orders left join customer on orders.o_custkey = customer.c_custkey+1;" >/dev/null
echo case9:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "select o_custkey from orders where o_totalprice > 151219 order by concat(o_orderkey, '0');" >/dev/null
echo case10:
time mysql -h 127.0.0.1 -P 4000 -u root -D test -Ne "update customer c  join orders o on o.o_custkey = c.c_custkey set c.c_comment = o.o_comment;" >/dev/null
