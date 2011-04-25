liblogistic_map.so: logistic_map.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -shared $< -o $@ -lgsl -lgslcblas

clean:
	-rm *.so
