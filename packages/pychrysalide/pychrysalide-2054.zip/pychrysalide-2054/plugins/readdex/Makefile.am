
lib_LTLIBRARIES = libreaddex.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif


libreaddex_la_SOURCES =						\
	class.h class.c							\
	code.h code.c							\
	header.h header.c						\
	ids.h ids.c								\
	reader.h reader.c

libreaddex_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libreaddex_la_LDFLAGS =							\
	-avoid-version								\
	-L$(top_srcdir)/src/.libs -lchrysacore		\
	-L$(top_srcdir)/plugins/dex/.libs -ldex		\
	-L$(top_srcdir)/plugins/fmtp/.libs -lfmtp	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libreaddex_la_SOURCES:%c=)
