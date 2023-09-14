
GTK3_CSS =								\
	palette.css							\
	tokens.css							\
	widgets.css

emacs.ctm: gresource.xml $(GTK3_CSS)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) gresource.xml

css_DATA = emacs.ctm

cssdir = $(themesdir)

EXTRA_DIST = $(css_DATA) gresource.xml

CLEANFILES = $(css_DATA)
