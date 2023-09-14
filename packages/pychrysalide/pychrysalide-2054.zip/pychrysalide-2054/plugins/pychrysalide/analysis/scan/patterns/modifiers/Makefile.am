
noinst_LTLIBRARIES = libpychrysaanalysisscanpatternsmodifiers.la

libpychrysaanalysisscanpatternsmodifiers_la_SOURCES = \
	hex.h hex.c								\
	list.h list.c							\
	module.h module.c						\
	plain.h plain.c							\
	rev.h rev.c

libpychrysaanalysisscanpatternsmodifiers_la_CFLAGS = $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) $(TOOLKIT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisscanpatternsmodifiers_la_SOURCES:%c=)
