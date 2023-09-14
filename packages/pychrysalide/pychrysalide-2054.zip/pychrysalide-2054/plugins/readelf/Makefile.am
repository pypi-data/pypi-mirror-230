
lib_LTLIBRARIES = libreadelf.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif


libreadelf_la_SOURCES =						\
	header.h header.c						\
	program.h program.c						\
	reader.h reader.c						\
	section.h section.c						\
	strtab.h strtab.c

libreadelf_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libreadelf_la_LDFLAGS =							\
	-avoid-version								\
	-L$(top_srcdir)/src/.libs -lchrysacore		\
	-L$(top_srcdir)/plugins/elf/.libs -lelf		\
	-L$(top_srcdir)/plugins/fmtp/.libs -lfmtp	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libreadelf_la_SOURCES:%c=)
