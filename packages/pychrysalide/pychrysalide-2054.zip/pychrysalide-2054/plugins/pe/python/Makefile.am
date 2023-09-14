
noinst_LTLIBRARIES = libpepython.la

libpepython_la_SOURCES =					\
	constants.h constants.c					\
	format.h format.c						\
	module.h module.c						\
	routine.h routine.c						\
	translate.h translate.c

libpepython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpepython_la_SOURCES:%c=)
