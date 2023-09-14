
noinst_LTLIBRARIES  = libanalysisdbitems.la

libanalysisdbitems_la_SOURCES =			\
	bookmark.h bookmark.c				\
	comment.h comment.c					\
	move.h move.c						\
	switcher.h switcher.c

libanalysisdbitems_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBSQLITE_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisdbitems_la_SOURCES:%c=)
