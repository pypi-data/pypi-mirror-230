
noinst_LTLIBRARIES = libpychrysaanalysisdbitems.la

libpychrysaanalysisdbitems_la_SOURCES =		\
	bookmark.h bookmark.c					\
	comment.h comment.c						\
	constants.h constants.c					\
	module.h module.c						\
	switcher.h switcher.c

libpychrysaanalysisdbitems_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisdbitems_la_SOURCES:%c=)
