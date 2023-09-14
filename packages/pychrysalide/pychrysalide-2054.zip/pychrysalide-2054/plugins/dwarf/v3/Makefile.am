
noinst_LTLIBRARIES = libdwarfv3.la

libdwarfv3_la_SOURCES =						\
	checks.h checks.c

libdwarfv3_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdwarfv3_la_SOURCES:%c=)
