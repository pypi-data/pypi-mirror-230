
noinst_LTLIBRARIES = libpychrysaguicore.la

libpychrysaguicore_la_SOURCES =				\
	global.h global.c						\
	items.h items.c							\
	module.h module.c						\
	panels.h panels.c

libpychrysaguicore_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaguicore_la_SOURCES:%c=)
