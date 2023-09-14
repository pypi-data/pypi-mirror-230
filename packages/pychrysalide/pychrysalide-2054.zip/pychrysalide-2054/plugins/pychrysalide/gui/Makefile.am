
noinst_LTLIBRARIES = libpychrysagui.la

libpychrysagui_la_SOURCES =					\
	constants.h constants.c					\
	item.h item.c							\
	menubar.h menubar.c						\
	module.h module.c						\
	panel.h panel.c

libpychrysagui_la_LIBADD =					\
	core/libpychrysaguicore.la				\
	panels/libpychrysaguipanels.la

libpychrysagui_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysagui_la_SOURCES:%c=)


SUBDIRS = core panels
