
noinst_LTLIBRARIES  = libguitb.la

libguitb_la_SOURCES =					\
	portions.h portions.c				\
	tbitem-int.h						\
	tbitem.h tbitem.c

libguitb_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libguitb_la_SOURCES:%c=)
