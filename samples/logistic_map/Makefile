liblogistic_map.so: logistic_map.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -lgsl -lgslcblas -Wall -Wextra -shared $< -o $@

clean:
	-rm *.so
