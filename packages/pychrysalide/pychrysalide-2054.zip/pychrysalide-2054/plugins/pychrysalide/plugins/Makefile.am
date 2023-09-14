
noinst_LTLIBRARIES = libpychrysaplugins.la

libpychrysaplugins_la_SOURCES =				\
	constants.h constants.c					\
	plugin.h plugin.c						\
	module.h module.c						\
	translate.h translate.c

libpychrysaplugins_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaplugins_la_SOURCES:%c=)
