
lib_LTLIBRARIES = liblnxsyscalls.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs:$$ORIGIN'

else

RUN_PATH = -Wl,-rpath,'$$ORIGIN'

endif

liblnxsyscalls_la_SOURCES =					\
	collect.h collect.c						\
	core.h core.c							\
	db.h db.c								\
	hops.h									\
	hops_armv7.h hops_armv7.c				\
	hunter.h hunter.c						\
	syscall.h syscall.c						\
	writer.h writer.c

liblnxsyscalls_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

liblnxsyscalls_la_LDFLAGS =					\
	-avoid-version							\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	-L$(top_srcdir)/plugins/arm/.libs -larm	\
	$(RUN_PATH)


EXTRA_DIST = linux-syscalls.db


db_DATA = linux-syscalls.db

dbdir = $(pluginsdatadir)


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(liblnxsyscalls_la_SOURCES:%c=)
