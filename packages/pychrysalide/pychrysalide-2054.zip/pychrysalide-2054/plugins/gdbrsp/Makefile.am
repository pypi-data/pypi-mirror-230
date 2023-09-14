
noinst_LTLIBRARIES = libdebuggdbrsp.la

libdebuggdbrsp_la_SOURCES =				\
	aops.h								\
	gdb-int.h							\
	gdb.h gdb.c							\
	helpers.h helpers.c					\
	helpers_arm.h helpers_arm.c			\
	helpers_arm64.h helpers_arm64.c		\
	packet.h packet.c					\
	stream-int.h						\
	stream.h stream.c					\
	support.h support.c					\
	target.h target.c					\
	tcp.h tcp.c							\
	utils.h utils.c

libdebuggdbrsp_la_LIBADD = 

libdebuggdbrsp_la_LDFLAGS =					\
	-L$(top_srcdir)/src/.libs -lchrysacore


devdir = $(includedir)/chrysalide/$(subdir:src/%=%)

dev_HEADERS = $(libdebuggdbrsp_la_SOURCES:%c=)


AM_CPPFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS) $(COMPLIANCE_FLAGS)
