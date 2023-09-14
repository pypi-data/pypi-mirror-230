
DEFAULT_INCLUDES = -I$(top_builddir) -idirafter.

lib_LTLIBRARIES = pychrysalide.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/chrysalide-libs'

endif


if BUILD_GTK_SUPPORT

GTKEXT_LIBADD =								\
	gtkext/libpychrysagtkext.la

GTKEXT_SUBDIR = 							\
	gtkext

GUI_LIBADD =								\
	gui/libpychrysagui.la

GUI_SUBDIR =								\
	gui

endif


pychrysalide_la_SOURCES =					\
	access.h access.c						\
	core.h core.c							\
	helpers.h helpers.c						\
	star.h star.c							\
	strenum.h strenum.c						\
	struct.h struct.c

AM_CFLAGS = $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT

pychrysalide_la_LIBADD =					\
	analysis/libpychrysaanalysis.la			\
	arch/libpychrysaarch.la					\
	common/libpychrysacommon.la				\
	core/libpychrysacore.la					\
	debug/libpychrysadebug.la				\
	format/libpychrysaformat.la				\
	glibext/libpychrysaglibext.la			\
	$(GTKEXT_LIBADD)						\
	$(GUI_LIBADD)							\
	mangling/libpychrysamangling.la			\
	plugins/libpychrysaplugins.la

# -ldl: dladdr(), dlerror()
pychrysalide_la_LDFLAGS =					\
	-module -avoid-version -ldl				\
	$(LIBPYTHON_INTERPRETER_LIBS)			\
	$(LIBPYGOBJECT_LIBS)					\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(pychrysalide_la_SOURCES:%c=)


SUBDIRS = analysis arch common core debug format glibext $(GTKEXT_SUBDIR) $(GUI_SUBDIR) mangling plugins
