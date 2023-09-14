
noinst_LTLIBRARIES = libdebug.la

libdebug_la_SOURCES =					\
	break-int.h							\
	break.h break.c						\
	debugger-int.h						\
	debugger.h debugger.c				\
	misc.h								\
	packet-int.h						\
	packet.h packet.c					\
	stream-int.h						\
	stream.h stream.c

libdebug_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libdebug_la_SOURCES:%c=)
