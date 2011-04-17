objs=kaplan_yorke_map.o
slib=libkaplan_yorke_map.so

all: $(slib)

libkaplan_yorke_map.so: kaplan_yorke_map.o
	gcc -shared -o $@ $<

kaplan_yorke_map.o: kaplan_yorke_map.c
	gcc -c $< -fPIC -O3 -ftree-vectorizer-verbose=1

clean:
	-rm $(objs) $(slib)

.PHONY: all clean
