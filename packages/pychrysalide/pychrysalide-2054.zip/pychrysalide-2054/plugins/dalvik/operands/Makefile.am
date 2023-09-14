
noinst_LTLIBRARIES = libdalvikoperands.la

libdalvikoperands_la_SOURCES =				\
	args.h args.c							\
	pool.h pool.c							\
	register.h register.c

libdalvikoperands_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdalvikoperands_la_SOURCES:%c=)
