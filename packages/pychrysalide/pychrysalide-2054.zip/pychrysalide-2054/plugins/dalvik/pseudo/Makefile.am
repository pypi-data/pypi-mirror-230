
noinst_LTLIBRARIES = libdalvikpseudo.la

libdalvikpseudo_la_SOURCES =				\
	fill.h fill.c							\
	identifiers.h							\
	switch.h switch.c

libdalvikpseudo_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdalvikpseudo_la_SOURCES:%c=)
