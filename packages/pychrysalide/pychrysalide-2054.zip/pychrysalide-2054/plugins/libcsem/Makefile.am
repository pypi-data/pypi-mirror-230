
lib_LTLIBRARIES = liblibcsem.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif


liblibcsem_la_SOURCES =						\
	exit.h exit.c							\
	semantic.h semantic.c

liblibcsem_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

liblibcsem_la_LDFLAGS =						\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	-L$(top_srcdir)/plugins/elf/.libs -lelf	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(liblibcsem_la_SOURCES:%c=)
