
noinst_LTLIBRARIES  = libanalysisscanmatches.la


libanalysisscanmatches_la_SOURCES =		\
	bytes-int.h							\
	bytes.h bytes.c						\
	pending.h pending.c

libanalysisscanmatches_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanmatches_la_SOURCES:%c=)
