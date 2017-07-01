update customer c  join orders o on o.o_custkey = c.c_custkey set c.c_comment = o.o_comment;

