
noinst_LTLIBRARIES = libwinordinalspython.la

libwinordinalspython_la_SOURCES =			\
	module.h module.c

libwinordinalspython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libwinordinalspython_la_SOURCES:%c=)
