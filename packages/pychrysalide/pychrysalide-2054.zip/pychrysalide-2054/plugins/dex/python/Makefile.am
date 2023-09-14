
noinst_LTLIBRARIES = libdexpython.la

libdexpython_la_SOURCES =					\
	class.h class.c							\
	constants.h constants.c					\
	field.h field.c							\
	format.h format.c						\
	method.h method.c						\
	module.h module.c						\
	pool.h pool.c							\
	routine.h routine.c						\
	translate.h translate.c

libdexpython_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdexpython_la_SOURCES:%c=)
