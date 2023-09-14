
noinst_LTLIBRARIES = libpychrysaanalysisscanpatternsbackends.la

libpychrysaanalysisscanpatternsbackends_la_SOURCES =		\
	acism.h acism.c							\
	bitap.h bitap.c							\
	module.h module.c

libpychrysaanalysisscanpatternsbackends_la_CFLAGS = $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) $(TOOLKIT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisscanpatternsbackends_la_SOURCES:%c=)
