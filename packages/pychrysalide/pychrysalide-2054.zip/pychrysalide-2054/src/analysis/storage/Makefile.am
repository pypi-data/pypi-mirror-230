
noinst_LTLIBRARIES  = libanalysisstorage.la


libanalysisstorage_la_SOURCES =				\
	cache-int.h								\
	cache.h cache.c							\
	container-int.h							\
	container.h container.c					\
	serialize-int.h							\
	serialize.h serialize.c					\
	storage-int.h							\
	storage.h storage.c						\
	tpmem.h tpmem.c

libanalysisstorage_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisstorage_la_SOURCES:%c=)
