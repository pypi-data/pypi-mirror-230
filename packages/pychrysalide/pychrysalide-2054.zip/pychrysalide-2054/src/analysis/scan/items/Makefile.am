
noinst_LTLIBRARIES  = libanalysisscanitems.la


if BUILD_MAGIC_SUPPORT

MAGIC_LIBADD = magic/libanalysisscanitemsmagic.la

MAGIC_SUBDIRS = magic

endif


libanalysisscanitems_la_SOURCES =			\
	count.h count.c							\
	datasize.h datasize.c					\
	uint-int.h								\
	uint.h uint.c

libanalysisscanitems_la_LIBADD = 			\
	console/libanalysisscanitemsconsole.la	\
	$(MAGIC_LIBADD)							\
	math/libanalysisscanitemsmath.la		\
	string/libanalysisscanitemsstring.la	\
	time/libanalysisscanitemstime.la

libanalysisscanitems_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanitems_la_SOURCES:%c=)


SUBDIRS = console $(MAGIC_SUBDIRS) math string time
