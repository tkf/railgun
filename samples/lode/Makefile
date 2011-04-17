.PHONY: all
all: liblode.so liblode_cfuncprefix.so

liblode.so: lode.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared $< -o $@

liblode_cfuncprefix.so: lode_cfuncprefix.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared $< -o $@

clean:
	rm *.so
