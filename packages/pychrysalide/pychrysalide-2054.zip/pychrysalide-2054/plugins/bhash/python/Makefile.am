
noinst_LTLIBRARIES = libbhashpython.la

libbhashpython_la_SOURCES =					\
	imphash.h imphash.c						\
	module.h module.c						\
	tlsh.h tlsh.c							\
	rich.h rich.c

libbhashpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libbhashpython_la_SOURCES:%c=)
