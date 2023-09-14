
noinst_LTLIBRARIES = libpychrysaanalysisstorage.la

libpychrysaanalysisstorage_la_SOURCES =		\
	cache.h cache.c							\
	container.h container.c					\
	module.h module.c						\
	serialize.h serialize.c					\
	storage.h storage.c						\
	tpmem.h tpmem.c

libpychrysaanalysisstorage_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisstorage_la_SOURCES:%c=)
