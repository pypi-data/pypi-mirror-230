
noinst_LTLIBRARIES  = libguimenus.la

libguimenus_la_SOURCES =				\
	binary.h binary.c					\
	debug.h debug.c						\
	edition.h edition.c					\
	file.h file.c						\
	help.h help.c						\
	options.h options.c					\
	project.h project.c					\
	view.h view.c

libguimenus_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libguimenus_la_SOURCES:%c=)
