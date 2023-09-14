
noinst_LTLIBRARIES = libpychrysamangling.la

libpychrysamangling_la_SOURCES =			\
	demangler.h demangler.c					\
	module.h module.c

libpychrysamangling_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysamangling_la_SOURCES:%c=)
