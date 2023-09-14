
lib_LTLIBRARIES = libspeed.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif


libspeed_la_SOURCES =						\
	speed.h speed.c

libspeed_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libspeed_la_LDFLAGS =						\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libspeed_la_SOURCES:%c=)
