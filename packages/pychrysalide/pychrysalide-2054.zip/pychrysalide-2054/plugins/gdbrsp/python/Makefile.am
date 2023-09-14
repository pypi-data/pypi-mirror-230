
noinst_LTLIBRARIES = libpychrysadebuggdbrsp.la

libpychrysadebuggdbrsp_la_SOURCES =		\
	gdb.h gdb.c							\
	module.h module.c

libpychrysadebuggdbrsp_la_LDFLAGS = 


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysadebuggdbrsp_la_SOURCES:%c=)


AM_CPPFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS) $(COMPLIANCE_FLAGS)
