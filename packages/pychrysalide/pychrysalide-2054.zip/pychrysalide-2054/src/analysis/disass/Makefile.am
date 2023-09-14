
noinst_LTLIBRARIES = libanalysisdisass.la

libanalysisdisass_la_SOURCES =			\
	area.h area.c						\
	block.h block.c						\
	disassembler.h disassembler.c		\
	dragon.h dragon.c					\
	fetch.h fetch.c						\
	instructions.h instructions.c		\
	limit.h limit.c						\
	links.h links.c						\
	loop.h loop.c						\
	output.h output.c					\
	rank.h rank.c						\
	routines.h routines.c

libanalysisdisass_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisdisass_la_SOURCES:%c=)
