select * from orders left join customer on orders.o_custkey = customer.c_custkey+1;
