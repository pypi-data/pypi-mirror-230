
noinst_LTLIBRARIES  = libanalysisscanitemstime.la


libanalysisscanitemstime_la_SOURCES =		\
	make.h make.c							\
	now.h now.c

libanalysisscanitemstime_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanitemstime_la_SOURCES:%c=)
