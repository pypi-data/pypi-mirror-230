
noinst_LTLIBRARIES  = libanalysisscanpatternstokens.la


libanalysisscanpatternstokens_la_SOURCES =	\
	atom.h atom.c							\
	hex-int.h								\
	hex.h hex.c								\
	node-int.h								\
	node.h node.c							\
	offset.h offset.c						\
	plain-int.h								\
	plain.h plain.c

libanalysisscanpatternstokens_la_LIBADD = 		\
	nodes/libanalysisscanpatternstokensnodes.la

libanalysisscanpatternstokens_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanpatternstokens_la_SOURCES:%c=)


SUBDIRS = nodes
