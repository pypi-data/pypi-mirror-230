
noinst_LTLIBRARIES = libpychrysaglibext.la

libpychrysaglibext_la_SOURCES =				\
	constants.h constants.c					\
	binarycursor.h binarycursor.c			\
	binportion.h binportion.c				\
	buffercache.h buffercache.c				\
	bufferline.h bufferline.c				\
	comparison.h comparison.c				\
	configuration.h configuration.c			\
	linecursor.h linecursor.c				\
	linegen.h linegen.c						\
	module.h module.c						\
	singleton.h singleton.c

if BUILD_GTK_SUPPORT

libpychrysaglibext_la_SOURCES +=			\
	bufferview.h bufferview.c				\
	loadedpanel.h loadedpanel.c				\
	named.h named.c

endif

libpychrysaglibext_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaglibext_la_SOURCES:%c=)
