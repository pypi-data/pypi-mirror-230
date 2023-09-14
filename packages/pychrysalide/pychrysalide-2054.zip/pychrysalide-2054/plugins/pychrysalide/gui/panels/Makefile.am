
noinst_LTLIBRARIES = libpychrysaguipanels.la

libpychrysaguipanels_la_SOURCES =			\
	module.h module.c						\
	updating.h updating.c

libpychrysaguipanels_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaguipanels_la_SOURCES:%c=)
