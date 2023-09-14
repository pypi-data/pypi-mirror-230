
noinst_LTLIBRARIES = libarmpythonv7.la

libarmpythonv7_la_SOURCES =					\
	instruction.h instruction.c				\
	module.h module.c						\
	processor.h processor.c

libarmpythonv7_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libarmpythonv7_la_SOURCES:%c=)
