
noinst_LTLIBRARIES = libkaitaipythonrecords.la

libkaitaipythonrecords_la_SOURCES = 		\
	empty.h empty.c							\
	group.h group.c							\
	item.h item.c							\
	list.h list.c							\
	module.h module.c						\
	value.h value.c

libkaitaipythonrecords_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide-$(subdir)

dev_HEADERS = $(libkaitaipythonrecords_la_SOURCES:%c=)
