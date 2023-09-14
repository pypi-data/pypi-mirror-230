
noinst_LTLIBRARIES  = libanalysishuman.la


libanalysishuman_la_SOURCES =			\
	lang-int.h							\
	lang.h lang.c

libanalysishuman_la_CFLAGS = $(TOOLKIT_CFLAGS)

libanalysishuman_la_LIBADD =			\
	asm/libanalysishumanasm.la


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysishuman_la_SOURCES:%c=)


SUBDIRS = asm
