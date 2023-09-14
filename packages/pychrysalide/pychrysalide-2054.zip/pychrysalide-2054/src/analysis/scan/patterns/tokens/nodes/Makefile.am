
noinst_LTLIBRARIES  = libanalysisscanpatternstokensnodes.la


libanalysisscanpatternstokensnodes_la_SOURCES =	\
	any-int.h								\
	any.h any.c								\
	choice-int.h							\
	choice.h choice.c						\
	masked-int.h							\
	masked.h masked.c						\
	not-int.h								\
	not.h not.c								\
	plain-int.h								\
	plain.h plain.c							\
	sequence-int.h							\
	sequence.h sequence.c

libanalysisscanpatternstokensnodes_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanpatternstokensnodes_la_SOURCES:%c=)
