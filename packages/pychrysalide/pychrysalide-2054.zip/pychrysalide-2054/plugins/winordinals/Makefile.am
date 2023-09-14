
lib_LTLIBRARIES = libwinordinals.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libwinordinalspython.la

if BUILD_DISCARD_LOCAL

if BUILD_PYTHON_PACKAGE
PYTHON3_RUN_PATH = -Wl,-rpath,'$$ORIGIN/..'
else
PYTHON3_RUN_PATH = -Wl,-rpath,'$$ORIGIN'
endif

else

PYTHON3_RUN_PATH = -Wl,-rpath,$(abs_top_srcdir)/plugins/pychrysalide/.libs

endif

PYTHON3_LDFLAGS = $(PYTHON3_RUN_PATH) -L$(top_srcdir)/plugins/pychrysalide/.libs -l:pychrysalide.so

PYTHON3_SUBDIRS = python

endif


libwinordinals_la_SOURCES =					\
	assign.h assign.c						\
	cache_oleaut32.h cache_oleaut32.c		\
	cache_ws2_32.h cache_ws2_32.c			\
	cache_wsock32.h cache_wsock32.c			\
	core.h core.c							\
	ordinals.h ordinals.c

libwinordinals_la_LIBADD =					\
	$(PYTHON3_LIBADD)

libwinordinals_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libwinordinals_la_LDFLAGS =					\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	-L$(top_srcdir)/plugins/pe/.libs -lpe	\
	$(RUN_PATH) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libwinordinals_la_SOURCES:%c=)


SUBDIRS = $(PYTHON3_SUBDIRS)
