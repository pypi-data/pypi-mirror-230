
lib_LTLIBRARIES = libropgadgets.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif


libropgadgets_la_SOURCES =				\
	finder.h finder.c					\
	helper.h helper.c					\
	helper_arm.h helper_arm.c			\
	plugin.h plugin.c					\
	select.h select.c

libropgadgets_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libropgadgets_la_LDFLAGS =					\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	-L$(top_srcdir)/plugins/arm/.libs -larm	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libropgadgets_la_SOURCES:%c=)
