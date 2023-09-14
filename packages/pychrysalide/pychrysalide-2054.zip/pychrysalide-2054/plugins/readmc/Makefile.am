
lib_LTLIBRARIES = libreadmc.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif


libreadmc_la_SOURCES =						\
	header.h header.c						\
	reader.h reader.c						\
	text.h text.c							\
	v21.h v21.c								\
	v23.h v23.c								\
	v24.h v24.c

libreadmc_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libreadmc_la_LDFLAGS =									\
	-avoid-version										\
	-L$(top_srcdir)/src/.libs -lchrysacore				\
	-L$(top_srcdir)/plugins/mobicore/.libs -lmobicore	\
	-L$(top_srcdir)/plugins/fmtp/.libs -lfmtp			\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libreadmc_la_SOURCES:%c=)
