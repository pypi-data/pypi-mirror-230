
noinst_LTLIBRARIES = libdwarfv4.la

libdwarfv4_la_SOURCES =						\
	checks.h checks.c

libdwarfv4_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdwarfv4_la_SOURCES:%c=)
