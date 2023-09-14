
lib_LTLIBRARIES = libbootimg.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libbootimgpython.la

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


libbootimg_la_SOURCES =						\
	core.h core.c							\
	bootimg-def.h							\
	format-int.h format-int.c				\
	format.h format.c

libbootimg_la_LIBADD =						\
	$(PYTHON3_LIBADD)

libbootimg_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libbootimg_la_LDFLAGS =						\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libbootimg_la_SOURCES:%c=)


SUBDIRS = $(PYTHON3_SUBDIRS)
