
noinst_LTLIBRARIES = libpychrysacore.la

libpychrysacore_la_SOURCES =				\
	constants.h constants.c					\
	demanglers.h demanglers.c				\
	global.h global.c						\
	logs.h logs.c							\
	module.h module.c						\
	params.h params.c						\
	processors.h processors.c				\
	queue.h queue.c

libpychrysacore_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysacore_la_SOURCES:%c=)
