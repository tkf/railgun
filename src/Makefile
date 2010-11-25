# this Makefile is only for syntax checking (flymake)

CHK_SOURCES=$(shell find . -name '*.c')
python_include=$(shell python -c 'import distutils.sysconfig; print distutils.sysconfig.get_python_inc()')

CHECKSYNTAX.c = $(CC) $(CFLAGS) $(CPPFLAGS) -Wall -Wextra -pedantic -fsyntax-only -I${python_include}

check-syntax: $(addsuffix -check-syntax,$(CHK_SOURCES))

%.c-check-syntax:
	$(CHECKSYNTAX.c) $*.c
