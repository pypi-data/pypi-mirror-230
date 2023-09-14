
noinst_LTLIBRARIES = libdexbnfpython.la

libdexbnfpython_la_SOURCES =				\
	demangler.h demangler.c					\
	module.h module.c

libdexbnfpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdexbnfpython_la_SOURCES:%c=)
