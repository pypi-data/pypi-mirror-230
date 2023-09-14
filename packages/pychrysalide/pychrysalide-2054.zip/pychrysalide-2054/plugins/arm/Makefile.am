
lib_LTLIBRARIES = libarm.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libarmpython.la

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


libarm_la_SOURCES =							\
	cond.h									\
	context-int.h							\
	context.h context.c						\
	core.h core.c							\
	instruction-int.h						\
	instruction.h instruction.c				\
	link.h link.c							\
	processor-int.h							\
	processor.h processor.c					\
	register-int.h							\
	register.h register.c

libarm_la_LIBADD =							\
	$(PYTHON3_LIBADD)						\
	v7/libarmv7.la

libarm_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libarm_la_LDFLAGS =							\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libarm_la_SOURCES:%c=)


SUBDIRS = v7 $(PYTHON3_SUBDIRS)
