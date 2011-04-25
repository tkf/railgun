.PHONY: all
all: liblode.so liblode_cfuncprefix.so

liblode.so: lode.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -shared $< -o $@

liblode_cfuncprefix.so: lode_cfuncprefix.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -shared $< -o $@

clean:
	-rm *.so
