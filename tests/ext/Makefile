compile_shared=$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared -fPIC

.PHONY: all
all: build/vectclac.so build/arrayaccess.so build/arrayaccess-c99.so

build/arrayaccess.so: build/arrayaccess.c
	${compile_shared} $< -o $@

build/arrayaccess-c99.so: build/arrayaccess.c
	${compile_shared} -std=c99 $< -o $@

build/vectclac.so: src/vectclac.c build/.dmy
	${compile_shared} $< -o $@

build/arrayaccess.c: src/gene_arrayaccess.py build/.dmy
	python $< $@

build/.dmy:
	mkdir -p build
	touch $@

.PHONY: clean
clean:
	rm -r build
