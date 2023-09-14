
noinst_LTLIBRARIES = libdwarfv2.la

libdwarfv2_la_SOURCES =						\
	checks.h checks.c

libdwarfv2_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdwarfv2_la_SOURCES:%c=)
