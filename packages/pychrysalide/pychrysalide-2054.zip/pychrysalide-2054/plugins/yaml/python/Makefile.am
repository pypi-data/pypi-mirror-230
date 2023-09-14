
noinst_LTLIBRARIES = libyamlpython.la

libyamlpython_la_SOURCES =					\
	collection.h collection.c				\
	constants.h constants.c					\
	module.h module.c						\
	node.h node.c							\
	pair.h pair.c							\
	parser.h parser.c

libyamlpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libyamlpython_la_SOURCES:%c=)
