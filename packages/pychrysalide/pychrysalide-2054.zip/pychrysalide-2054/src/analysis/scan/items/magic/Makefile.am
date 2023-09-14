
noinst_LTLIBRARIES  = libanalysisscanitemsmagic.la


libanalysisscanitemsmagic_la_SOURCES =		\
	cookie.h cookie.c						\
	mime-encoding.h mime-encoding.c			\
	mime-type.h mime-type.c					\
	type.h type.c

libanalysisscanitemsmagic_la_CFLAGS = $(LIBGOBJ_CFLAGS) $(LIBMAGIC_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanitemsmagic_la_SOURCES:%c=)
