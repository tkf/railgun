all: build/vectclac.so build/arrayaccess.so

build/arrayaccess.so: src/arrayaccess.c build/.dmy
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared $< -o $@

build/vectclac.so: src/vectclac.c build/.dmy
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared $< -o $@

build/.dmy:
	mkdir -p build
	touch $@

.PHONY: clean
clean:
	rm -r build
