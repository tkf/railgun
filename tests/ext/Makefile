compile_shared=$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -shared -fPIC

.PHONY: all
all: \
	build/vectclac.so build/vectclac-O3.so \
	build/arrayaccess.so build/arrayaccess-c99.so

build/arrayaccess.so: build/arrayaccess.c
	${compile_shared} $< -o $@

build/arrayaccess-c99.so: build/arrayaccess-c99.c
	${compile_shared} -std=c99 $< -o $@

build/vectclac.so: src/vectclac.c build/.dmy
	${compile_shared} $< -o $@

build/vectclac-O3.so: src/vectclac.c build/.dmy
	${compile_shared} -O3 $< -o $@

build/arrayaccess.c: src/gene_arrayaccess.py build/.dmy
	python $< $@

build/arrayaccess-c99.c: src/gene_arrayaccess.py build/.dmy
	python $< --c99 $@

build/.dmy:
	mkdir -p build
	touch $@

.PHONY: clean
clean:
	rm -r build
