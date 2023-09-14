
noinst_LTLIBRARIES = libdalvik35.la

libdalvik35_la_SOURCES =					\
	core.h core.c							\
	instruction.h instruction.c				\
	operand.h								\
	processor.h processor.c

libdalvik35_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libdalvik35_la_LIBADD =						\
	opcodes/libdalvik35opcodes.la


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libdalvik35_la_SOURCES:%c=)


SUBDIRS = opdefs opcodes
