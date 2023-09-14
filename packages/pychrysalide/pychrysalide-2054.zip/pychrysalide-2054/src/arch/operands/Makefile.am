
noinst_LTLIBRARIES = libarchoperands.la

libarchoperands_la_SOURCES =			\
	feeder-int.h						\
	feeder.h feeder.c					\
	immediate-int.h						\
	immediate.h immediate.c				\
	known.h known.c						\
	register-int.h						\
	register.h register.c				\
	proxy-int.h							\
	proxy.h proxy.c						\
	rename-int.h						\
	rename.h rename.c					\
	target-int.h						\
	target.h target.c					\
	targetable-int.h					\
	targetable.h targetable.c

libarchoperands_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libarchoperands_la_SOURCES:%c=)
