
lib_LTLIBRARIES = libmobicore.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif


libmobicore_la_SOURCES =					\
	core.h core.c							\
	mclf-def.h								\
	mclf-int.h mclf-int.c					\
	mclf.h mclf.c							\
	symbols.h symbols.c

libmobicore_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libmobicore_la_LDFLAGS =					\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libmobicore_la_SOURCES:%c=)
