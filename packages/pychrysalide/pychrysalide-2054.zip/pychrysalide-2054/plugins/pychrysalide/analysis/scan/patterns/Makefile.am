
noinst_LTLIBRARIES = libpychrysaanalysisscanpatterns.la

libpychrysaanalysisscanpatterns_la_SOURCES = \
	backend.h backend.c						\
	modifier.h modifier.c					\
	module.h module.c

libpychrysaanalysisscanpatterns_la_LIBADD = \
	backends/libpychrysaanalysisscanpatternsbackends.la \
	modifiers/libpychrysaanalysisscanpatternsmodifiers.la

libpychrysaanalysisscanpatterns_la_CFLAGS = $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
    $(TOOLKIT_CFLAGS) -I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisscanpatterns_la_SOURCES:%c=)


SUBDIRS = backends modifiers
