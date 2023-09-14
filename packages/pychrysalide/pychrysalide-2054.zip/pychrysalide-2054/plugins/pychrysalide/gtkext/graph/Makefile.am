
noinst_LTLIBRARIES = libpychrysagtkextgraph.la

libpychrysagtkextgraph_la_SOURCES =			\
	constants.h constants.c					\
	cluster.h cluster.c						\
	edge.h edge.c							\
	module.h module.c

libpychrysagtkextgraph_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysagtkextgraph_la_SOURCES:%c=)
