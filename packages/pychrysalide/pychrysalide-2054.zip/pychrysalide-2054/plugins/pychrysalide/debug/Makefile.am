
noinst_LTLIBRARIES = libpychrysadebug.la

libpychrysadebug_la_SOURCES =				\
	debugger.h debugger.c					\
	module.h module.c

libpychrysadebug_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysadebug_la_SOURCES:%c=)
