
BUILT_SOURCES = resources.h resources.c

noinst_LTLIBRARIES  = libgui.la

UI_FILES =								\
	editor.ui

libgui_la_SOURCES =						\
	agroup.h agroup.c					\
	editor.h editor.c					\
	item-int.h							\
	item.h item.c						\
	menubar.h menubar.c					\
	panel-int.h							\
	panel.h panel.c						\
	resources.h resources.c				\
	status.h status.c					\
	theme.h theme.c

libgui_la_LIBADD =						\
	core/libguicore.la					\
	dialogs/libguidialogs.la			\
	menus/libguimenus.la				\
	panels/libguipanels.la				\
	tb/libguitb.la

libgui_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libgui_la_SOURCES:%c=)


SUBDIRS = core dialogs menus panels tb


resources.c: gresource.xml $(UI_FILES)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-source --c-name gui gresource.xml

resources.h: gresource.xml
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) --generate-header --c-name gui gresource.xml


CLEANFILES = resources.h resources.c

EXTRA_DIST = gresource.xml $(UI_FILES)
