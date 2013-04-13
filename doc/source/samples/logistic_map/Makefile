liblogistic_map.so: logistic_map.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -fPIC -Wall -shared $< -o $@ -lgsl -lgslcblas

clean:
	-rm *.so
