liblogistic_map.so: logistic_map.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared $< -o $@ -lgsl -lgslcblas

clean:
	-rm *.so
