
noinst_LTLIBRARIES = libpychrysaarchinstructions.la

libpychrysaarchinstructions_la_SOURCES =	\
	constants.h constants.c					\
	module.h module.c						\
	raw.h raw.c								\
	undefined.h undefined.c

libpychrysaarchinstructions_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaarchinstructions_la_SOURCES:%c=)
