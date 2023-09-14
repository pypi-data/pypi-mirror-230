
noinst_LTLIBRARIES = libformat.la

libformat_la_SOURCES =					\
	debuggable-int.h					\
	debuggable.h debuggable.c			\
	executable-int.h executable-int.c	\
	executable.h executable.c			\
	flat-int.h							\
	flat.h flat.c						\
	format-int.h						\
	format.h format.c					\
	known-int.h							\
	known.h known.c						\
	preload-int.h						\
	preload.h preload.c					\
	strsym.h strsym.c					\
	symiter.h symiter.c					\
	symbol-int.h						\
	symbol.h symbol.c

libformat_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libformat_la_SOURCES:%c=)
