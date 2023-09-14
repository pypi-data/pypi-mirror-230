
noinst_LTLIBRARIES = libbootimgpython.la

libbootimgpython_la_SOURCES =				\
	format.h format.c						\
	module.h module.c						\
	translate.h translate.c

libbootimgpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libbootimgpython_la_SOURCES:%c=)
