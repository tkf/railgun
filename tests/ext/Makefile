build/vectclac.so: src/vectclac.c builddir
	$(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -shared $< -o $@

.PHONY: builddir
builddir:
	mkdir -p build
