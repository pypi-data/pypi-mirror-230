
noinst_LTLIBRARIES = libpychrysaanalysisscan.la

libpychrysaanalysisscan_la_SOURCES =		\
	constants.h constants.c					\
	context.h context.c						\
	core.h core.c							\
	expr.h expr.c							\
	item.h item.c							\
	module.h module.c						\
	options.h options.c						\
	scanner.h scanner.c						\
	space.h space.c

libpychrysaanalysisscan_la_LIBADD =			\
	patterns/libpychrysaanalysisscanpatterns.la

libpychrysaanalysisscan_la_CFLAGS = $(LIBPYTHON_CFLAGS) $(LIBPYGOBJECT_CFLAGS) $(TOOLKIT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysisscan_la_SOURCES:%c=)


SUBDIRS = patterns
