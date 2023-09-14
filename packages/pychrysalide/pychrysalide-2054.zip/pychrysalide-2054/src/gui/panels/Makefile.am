
DEFAULT_INCLUDES = -idirafter. -I$(top_builddir)

BUILT_SOURCES = resources.h resources.c

noinst_LTLIBRARIES  = libguipanels.la

UI_FILES =								\
	bintree.ui							\
	bookmarks.ui						\
	errors.ui							\
	glance.ui							\
	history.ui							\
	log.ui								\
	regedit.ui							\
	strings.ui							\
	symbols.ui							\
	welcome.ui

libguipanels_la_SOURCES =				\
	bintree.h bintree.c					\
	bookmarks.h bookmarks.c				\
	errors.h errors.c					\
	glance.h glance.c					\
	history.h history.c					\
	log.h log.c							\
	regedit.h regedit.c					\
	resources.h resources.c				\
	strings.h strings.c					\
	symbols.h symbols.c					\
	updating-int.h						\
	updating.h updating.c				\
	view.h view.c						\
	welcome.h welcome.c

libguipanels_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libguipanels_la_SOURCES:%c=)


resources.c: gresource.xml $(UI_FILES)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-source --c-name gui_panels gresource.xml

resources.h: gresource.xml
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-header --c-name gui_panels gresource.xml


CLEANFILES = resources.h resources.c

EXTRA_DIST = gresource.xml $(UI_FILES)
