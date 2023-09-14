
BUILT_SOURCES = resources.h resources.c

noinst_LTLIBRARIES  = libguidialogs.la

UI_FILES =								\
	about.ui							\
	bookmark.ui							\
	export_graph.ui						\
	identity.ui							\
	loading.ui							\
	preferences.ui						\
	prefs_fgraph.ui						\
	prefs_labels.ui						\
	snapshots.ui						\
	storage.ui

libguidialogs_la_SOURCES =				\
	about.h about.c						\
	bookmark.h bookmark.c				\
	export_disass.h export_disass.c		\
	export_graph.h export_graph.c		\
	goto.h goto.c						\
	gotox.h gotox.c						\
	identity.h identity.c				\
	loading.h loading.c					\
	preferences.h preferences.c			\
	prefs_fgraph.h prefs_fgraph.c		\
	prefs_labels.h prefs_labels.c		\
	resources.h resources.c				\
	snapshots.h snapshots.c				\
	storage.h storage.c

libguidialogs_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libguidialogs_la_SOURCES:%c=)


resources.c: gresource.xml $(UI_FILES)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-source --c-name gui_dialogs gresource.xml

resources.h: gresource.xml
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-header --c-name gui_dialogs gresource.xml


CLEANFILES = resources.h resources.c

EXTRA_DIST = gresource.xml $(UI_FILES)
