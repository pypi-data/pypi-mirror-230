
noinst_LTLIBRARIES  = libgtkextgraph.la

libgtkextgraph_la_SOURCES =				\
	cluster-int.h						\
	cluster.h cluster.c					\
	edge.h edge.c						\
	hspace.h hspace.c					\
	incoming.h incoming.c				\
	leaving.h leaving.c					\
	rank.h rank.c						\
	vspace.h vspace.c

libgtkextgraph_la_CFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(_la_SOURCES:%c=)
