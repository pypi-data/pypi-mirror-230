
noinst_LTLIBRARIES  = libglibextgenerators.la


libglibextgenerators_la_SOURCES =			\
	prologue.h prologue.c					\
	rborder.h rborder.c

if BUILD_GTK_SUPPORT

libglibextgenerators_la_SOURCES +=			\
	hex.h hex.c

endif

libglibextgenerators_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libglibextgenerators_la_SOURCES:%c=)
