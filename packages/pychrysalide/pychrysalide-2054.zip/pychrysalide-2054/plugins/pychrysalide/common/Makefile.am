
noinst_LTLIBRARIES = libpychrysacommon.la

libpychrysacommon_la_SOURCES =				\
	bits.h bits.c							\
	fnv1a.h fnv1a.c							\
	hex.h hex.c								\
	itoa.h itoa.c							\
	leb128.h leb128.c						\
	module.h module.c						\
	packed.h packed.c						\
	pathname.h pathname.c					\
	pearson.h pearson.c

libpychrysacommon_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysacommon_la_SOURCES:%c=)
