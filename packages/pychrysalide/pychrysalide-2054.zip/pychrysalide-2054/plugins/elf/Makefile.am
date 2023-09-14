
DEFAULT_INCLUDES = -idirafter. -I$(top_builddir)

lib_LTLIBRARIES = libelf.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libelfpython.la

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


libelf_la_SOURCES =							\
	core.h core.c							\
	elf-int.h elf-int.c						\
	elf_def.h								\
	elf_def_arm.h							\
	format.h format.c						\
	dynamic.h dynamic.c						\
	helper_arm.h helper_arm.c				\
	loading.h loading.c						\
	program.h program.c						\
	section.h section.c						\
	strings.h strings.c						\
	symbols.h symbols.c

libelf_la_LIBADD =							\
	$(PYTHON3_LIBADD)

libelf_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libelf_la_LDFLAGS =							\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH) $(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libelf_la_SOURCES:%c=)


SUBDIRS = $(PYTHON3_SUBDIRS)
