
DEFAULT_INCLUDES = -idirafter. -I$(top_builddir)

lib_LTLIBRARIES = libpe.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libpepython.la

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


libpe_la_SOURCES =							\
	core.h core.c							\
	pe-int.h pe-int.c						\
	format.h format.c						\
	pe_def.h								\
	rich.h rich.c							\
	routine.h routine.c						\
	section.h section.c						\
	symbols.h symbols.c

libpe_la_LIBADD =							\
	$(PYTHON3_LIBADD)

libpe_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libpe_la_LDFLAGS =							\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpe_la_SOURCES:%c=)


SUBDIRS = $(PYTHON3_SUBDIRS)
