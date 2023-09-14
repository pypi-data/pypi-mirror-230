
noinst_LTLIBRARIES  = libanalysisscanitemsmath.la


libanalysisscanitemsmath_la_SOURCES =		\
	to_string.h to_string.c

libanalysisscanitemsmath_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanitemsmath_la_SOURCES:%c=)
