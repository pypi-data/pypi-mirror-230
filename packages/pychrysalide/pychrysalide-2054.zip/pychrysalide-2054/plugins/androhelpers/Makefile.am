
lib_LTLIBRARIES = libandrohelpers.la

libdir = $(pluginslibdir)


libandrohelpers_la_SOURCES =			\
	androhelpers.h androhelpers.c		\
	params.h params.c					\
	try_n_catch.h try_n_catch.c			\
	switch.h switch.c

libandrohelpers_la_LDFLAGS =				\
	-L$(top_srcdir)/src/.libs -lchrysacore


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libandrohelpers_la_SOURCES:%c=)


AM_CPPFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS) $(COMPLIANCE_FLAGS)
