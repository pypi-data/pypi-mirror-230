
noinst_LTLIBRARIES = libdalvikpython.la

libdalvikpython_la_SOURCES =				\
	instruction.h instruction.c				\
	module.h module.c						\
	processor.h processor.c

libdalvikpython_la_LIBADD =					\
	v35/libdalvikpythonv35.la

libdalvikpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdalvikpython_la_SOURCES:%c=)


SUBDIRS = v35
