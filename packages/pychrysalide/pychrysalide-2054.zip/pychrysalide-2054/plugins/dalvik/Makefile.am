
lib_LTLIBRARIES = libdalvik.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libdalvikpython.la

if BUILD_DISCARD_LOCAL

if BUILD_PYTHON_PACKAGE
PYTHON3_RUN_PATH = -Wl,-rpath,'$$ORIGIN/..'
else
PYTHON3_RUN_PATH = -Wl,-rpath,'$$ORIGIN'
endif

else

PYTHON3_RUN_PATH = -Wl,-rpath,$(abs_top_srcdir)/plugins/pychrysalide/.libs

endif

PYTHON3_LDFLAGS = $(PYTHON3_RUN_PATH) -L$(top_srcdir)/plugins/pychrysalide/.libs -l:pychrysalide.so

PYTHON3_SUBDIRS = python

endif


libdalvik_la_SOURCES =						\
	context.h context.c						\
	core.h core.c							\
	fetch.h fetch.c							\
	helpers.h								\
	instruction-int.h						\
	instruction.h instruction.c				\
	link.h link.c							\
	operand.h operand.c						\
	post.h post.c							\
	processor-int.h							\
	processor.h processor.c					\
	register.h register.c

libdalvik_la_LIBADD =						\
	operands/libdalvikoperands.la			\
	pseudo/libdalvikpseudo.la				\
	$(PYTHON3_LIBADD)						\
	v35/libdalvik35.la

libdalvik_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libdalvik_la_LDFLAGS =						\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	-L$(top_srcdir)/plugins/dex/.libs -ldex	\
	$(RUN_PATH) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdalvik_la_SOURCES:%c=)


SUBDIRS = operands pseudo $(PYTHON3_SUBDIRS) v35
