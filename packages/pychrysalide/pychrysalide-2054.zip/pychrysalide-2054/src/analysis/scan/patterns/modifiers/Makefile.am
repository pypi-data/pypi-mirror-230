
noinst_LTLIBRARIES  = libanalysisscanpatternsmodifiers.la


libanalysisscanpatternsmodifiers_la_SOURCES = \
	hex.h hex.c								\
	list-int.h								\
	list.h list.c							\
	plain.h plain.c							\
	rev.h rev.c

libanalysisscanpatternsmodifiers_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanpatternsmodifiers_la_SOURCES:%c=)
