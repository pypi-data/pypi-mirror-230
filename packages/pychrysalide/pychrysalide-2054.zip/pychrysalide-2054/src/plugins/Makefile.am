
noinst_LTLIBRARIES = libplugins.la

libplugins_la_SOURCES =					\
	context-int.h						\
	context.h context.c					\
	dt.h dt.c							\
	pglist.h pglist.c					\
	plugin-def.h						\
	plugin-int.h						\
	plugin.h plugin.c					\
	self.h

libplugins_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libplugins_la_SOURCES:%c=)
