
noinst_LTLIBRARIES = libkaitaipythonparsers.la

libkaitaipythonparsers_la_SOURCES = 		\
	attribute.h attribute.c					\
	enum.h enum.c							\
	instance.h instance.c					\
	meta.h meta.c							\
	module.h module.c						\
	struct.h struct.c						\
	type.h type.c

libkaitaipythonparsers_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide-$(subdir)

dev_HEADERS = $(libkaitaipythonparsers_la_SOURCES:%c=)
