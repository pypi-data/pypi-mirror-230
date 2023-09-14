
noinst_LTLIBRARIES = libkaitairecords.la

libkaitairecords_la_SOURCES =				\
	empty-int.h								\
	empty.h empty.c							\
	group-int.h								\
	group.h group.c							\
	item-int.h								\
	item.h item.c							\
	list-int.h								\
	list.h list.c							\
	value-int.h								\
	value.h value.c

libkaitairecords_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide-$(subdir)

dev_HEADERS = $(libkaitairecords_la_SOURCES:%c=)
