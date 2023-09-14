
GTK3_CSS =								\
	palette.css							\
	tokens-light.css					\
	tokens-dark.css						\
	widgets-light.css					\
	widgets-dark.css

solarized.ctm: gresource.xml $(GTK3_CSS)
	glib-compile-resources --target=$@ --sourcedir=$(srcdir) gresource.xml

css_DATA = solarized.ctm

cssdir = $(themesdir)

EXTRA_DIST = $(css_DATA) gresource.xml

CLEANFILES = $(css_DATA)
