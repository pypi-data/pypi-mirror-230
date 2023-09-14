
noinst_LTLIBRARIES = libcore.la

libcore_la_SOURCES =					\
	collections.h collections.c			\
	columns.h							\
	core.h core.c						\
	demanglers.h demanglers.c			\
	global.h global.c					\
	logs.h logs.c						\
	nproc.h nproc.c						\
	params.h params.c					\
	paths.h paths.c						\
	processors.h processors.c			\
	queue.h queue.c

libcore_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libcore_la_SOURCES:%c=)
