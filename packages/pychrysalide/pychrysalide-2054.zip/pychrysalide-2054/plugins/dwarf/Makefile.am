
lib_LTLIBRARIES = libdwarf.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif


libdwarf_la_SOURCES =						\
	abbrev.h abbrev.c						\
	checks.h checks.c						\
	core.h core.c							\
	def.h									\
	die.h die.c								\
	form.h form.c							\
	format.h format.c						\
	info.h info.c							\
	utils.h utils.c


# libdwarf_la_SOURCES =					\
# 	abbrev.h abbrev.c					\
# 	die.h die.c							\
# 	dwarf.h dwarf.c						\
# 	dwarf-int.h dwarf-int.c				\
# 	dwarf_def.h							\
# 	form.h form.c						\
# 	info.h info.c						\
# 	symbols.h symbols.c

libdwarf_la_LIBADD =						\
	v2/libdwarfv2.la						\
	v3/libdwarfv3.la						\
	v4/libdwarfv4.la

libdwarf_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libdwarf_la_LDFLAGS =						\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(RUN_PATH)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdwarf_la_SOURCES:%c=)


SUBDIRS = v2 v3 v4
