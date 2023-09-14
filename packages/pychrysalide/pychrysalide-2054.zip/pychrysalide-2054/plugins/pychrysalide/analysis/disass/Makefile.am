
noinst_LTLIBRARIES = libpychrysaanalysisdisass.la

libpychrysaanalysisdisass_la_SOURCES =		\
	block.h block.c							\
	module.h module.c

libpychrysaanalysisdisass_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisdisass_la_SOURCES:%c=)
