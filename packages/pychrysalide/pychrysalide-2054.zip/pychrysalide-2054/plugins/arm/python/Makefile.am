
noinst_LTLIBRARIES = libarmpython.la

libarmpython_la_SOURCES =					\
	instruction.h instruction.c				\
	module.h module.c						\
	processor.h processor.c

libarmpython_la_LIBADD =					\
	v7/libarmpythonv7.la

libarmpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libarmpython_la_SOURCES:%c=)


SUBDIRS = v7
