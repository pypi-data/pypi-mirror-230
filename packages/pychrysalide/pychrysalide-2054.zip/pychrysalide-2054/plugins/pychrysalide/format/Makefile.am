
noinst_LTLIBRARIES = libpychrysaformat.la

libpychrysaformat_la_SOURCES =				\
	constants.h constants.c					\
	executable.h executable.c				\
	flat.h flat.c							\
	format.h format.c						\
	known.h known.c							\
	module.h module.c						\
	preload.h preload.c						\
	strsym.h strsym.c						\
	symbol.h symbol.c						\
	symiter.h symiter.c

libpychrysaformat_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaformat_la_SOURCES:%c=)
