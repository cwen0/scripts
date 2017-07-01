select sum(orders.o_totalprice) from orders left join customer on orders.o_custkey = customer.c_custkey;
