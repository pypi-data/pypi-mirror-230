
GTK3_CSS =								\
	core.css							\
	definition.xml						\
	display.css							\
	icons.css							\
	portions.css						\
	tokens-light.css					\
	tokens-dark.css						\
	widgets-light.css					\
	widgets-dark.css					\
	clean.png							\
	redo.png							\
	undo.png

adwaita.ctm: gresource.xml $(GTK3_CSS)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) gresource.xml

css_DATA = adwaita.ctm

cssdir = $(themesdir)

EXTRA_DIST = $(css_DATA) gresource.xml

CLEANFILES = $(css_DATA)
