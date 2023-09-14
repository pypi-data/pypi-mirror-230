
noinst_LTLIBRARIES  = libanalysisscanitemsstring.la


libanalysisscanitemsstring_la_SOURCES =		\
	lower.h lower.c							\
	to_int.h to_int.c						\
	upper.h upper.c

libanalysisscanitemsstring_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanitemsstring_la_SOURCES:%c=)
