
noinst_LTLIBRARIES = libpychrysaarchoperands.la

libpychrysaarchoperands_la_SOURCES =		\
	constants.h constants.c					\
	feeder.h feeder.c						\
	immediate.h immediate.c					\
	known.h known.c							\
	module.h module.c						\
	proxy.h proxy.c							\
	register.h register.c					\
	rename.h rename.c						\
	target.h target.c						\
	targetable.h targetable.c

libpychrysaarchoperands_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaarchoperands_la_SOURCES:%c=)
