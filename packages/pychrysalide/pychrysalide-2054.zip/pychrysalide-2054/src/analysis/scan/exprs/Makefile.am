
noinst_LTLIBRARIES  = libanalysisscanexprs.la


libanalysisscanexprs_la_SOURCES =			\
	access-int.h							\
	access.h access.c						\
	arithmetic-int.h						\
	arithmetic.h arithmetic.c				\
	call-int.h								\
	call.h call.c							\
	counter-int.h							\
	counter.h counter.c						\
	handler-int.h							\
	handler.h handler.c						\
	intersect-int.h							\
	intersect.h intersect.c					\
	item-int.h								\
	item.h item.c							\
	literal-int.h							\
	literal.h literal.c						\
	logical-int.h							\
	logical.h logical.c						\
	range-int.h								\
	range.h range.c							\
	relational-int.h						\
	relational.h relational.c				\
	set-int.h								\
	set.h set.c								\
	setcounter-int.h						\
	setcounter.h setcounter.c				\
	strop-int.h								\
	strop.h strop.c

libanalysisscanexprs_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanexprs_la_SOURCES:%c=)
