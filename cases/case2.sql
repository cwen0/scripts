select * from orders where exists (select * from customer where orders.o_custkey = customer.c_custkey);
