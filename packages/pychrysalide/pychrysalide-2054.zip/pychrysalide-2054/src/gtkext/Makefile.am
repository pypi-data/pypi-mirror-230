
BUILT_SOURCES = resources.h resources.c

noinst_LTLIBRARIES = libgtkext.la

UI_FILES =								\
	blockbar.ui

libgtkext_la_SOURCES =						\
	diagram.h diagram.c						\
	easygtk.h easygtk.c						\
	gtkbinarystrip.h gtkbinarystrip.c		\
	gtkblockdisplay.h gtkblockdisplay.c		\
	gtkbufferdisplay-int.h					\
	gtkbufferdisplay.h gtkbufferdisplay.c	\
	gtkdisplaypanel-int.h					\
	gtkdisplaypanel.h gtkdisplaypanel.c		\
	gtkdockable-int.h						\
	gtkdockable.h gtkdockable.c				\
	gtkdockstation.h gtkdockstation.c		\
	gtkgraphdisplay.h gtkgraphdisplay.c		\
	gtkstatusstack.h gtkstatusstack.c		\
	hexdisplay.h hexdisplay.c				\
	named-int.h								\
	named.h named.c							\
	rendering.h rendering.c					\
	resources.h resources.c					\
	support.h support.c						\
	tiledgrid.h tiledgrid.c					\
	tmgt.h tmgt.c

libgtkext_la_LIBADD = 					\
	graph/libgtkextgraph.la

libgtkext_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libgtkext_la_SOURCES:%c=)


SUBDIRS = graph


resources.c: gresource.xml $(UI_FILES)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-source --c-name gtkext gresource.xml

resources.h: gresource.xml
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-header --c-name gtkext gresource.xml


CLEANFILES = resources.h resources.c

EXTRA_DIST = gresource.xml $(UI_FILES)
