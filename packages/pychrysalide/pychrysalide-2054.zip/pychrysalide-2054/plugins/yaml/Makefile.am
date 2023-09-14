
lib_LTLIBRARIES = libyaml.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libyamlpython.la

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


libyaml_la_SOURCES =						\
	collection-int.h						\
	collection.h collection.c				\
	core.h core.c							\
	node-int.h								\
	node.h node.c							\
	pair-int.h								\
	pair.h pair.c							\
	parser.h parser.c

libyaml_la_LIBADD =							\
	$(PYTHON3_LIBADD)

libyaml_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBYAML_CFLAGS) -I$(top_srcdir)/src

libyaml_la_LDFLAGS =						\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH) $(LIBYAML_LIBS) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libyaml_la_SOURCES:%c=)


SUBDIRS = $(PYTHON3_SUBDIRS)
