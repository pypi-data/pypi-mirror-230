
noinst_LTLIBRARIES  = libanalysisscanitemsconsole.la


libanalysisscanitemsconsole_la_SOURCES =	\
	log.h log.c

libanalysisscanitemsconsole_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanitemsconsole_la_SOURCES:%c=)
