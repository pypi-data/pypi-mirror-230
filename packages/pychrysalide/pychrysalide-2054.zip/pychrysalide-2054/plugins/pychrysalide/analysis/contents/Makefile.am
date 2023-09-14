
noinst_LTLIBRARIES = libpychrysaanalysiscontents.la

libpychrysaanalysiscontents_la_SOURCES = 	\
	encapsulated.h encapsulated.c			\
	file.h file.c							\
	memory.h memory.c						\
	module.h module.c						\
	restricted.h restricted.c

libpychrysaanalysiscontents_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysiscontents_la_SOURCES:%c=)
