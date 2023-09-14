
noinst_LTLIBRARIES = libarchinstructions.la

libarchinstructions_la_SOURCES =			\
	raw.h raw.c								\
	undefined-int.h							\
	undefined.h undefined.c

libarchinstructions_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libarchinstructions_la_SOURCES:%c=)
