
noinst_LTLIBRARIES = libpychrysagtkext.la

libpychrysagtkext_la_SOURCES =				\
	blockdisplay.h blockdisplay.c			\
	bufferdisplay.h bufferdisplay.c			\
	displaypanel.h displaypanel.c			\
	dockable.h dockable.c					\
	easygtk.h easygtk.c						\
	module.h module.c						\
	named.h named.c

libpychrysagtkext_la_LIBADD =				\
	graph/libpychrysagtkextgraph.la

libpychrysagtkext_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysagtkext_la_SOURCES:%c=)


SUBDIRS = graph
