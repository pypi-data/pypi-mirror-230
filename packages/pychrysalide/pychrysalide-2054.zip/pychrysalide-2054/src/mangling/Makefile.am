
noinst_LTLIBRARIES = libmangling.la

libmangling_la_SOURCES =				\
	context-int.h						\
	context.h context.c					\
	demangler-int.h						\
	demangler.h demangler.c

libmangling_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libmangling_la_SOURCES:%c=)
