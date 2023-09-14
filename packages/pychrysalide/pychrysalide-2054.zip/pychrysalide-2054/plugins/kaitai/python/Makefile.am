
noinst_LTLIBRARIES = libkaitaipython.la

libkaitaipython_la_SOURCES =				\
	array.h array.c							\
	module.h module.c						\
	parser.h parser.c						\
	record.h record.c						\
	scope.h scope.c							\
	stream.h stream.c

libkaitaipython_la_LIBADD =					\
	parsers/libkaitaipythonparsers.la		\
	records/libkaitaipythonrecords.la

libkaitaipython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide-$(subdir)

dev_HEADERS = $(libkaitaipython_la_SOURCES:%c=)


SUBDIRS = parsers records
