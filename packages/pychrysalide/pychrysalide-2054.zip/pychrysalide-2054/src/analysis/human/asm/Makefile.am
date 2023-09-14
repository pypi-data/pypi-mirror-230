
noinst_LTLIBRARIES  = libanalysishumanasm.la


libanalysishumanasm_la_SOURCES =		\
	lang.h lang.c

libanalysishumanasm_la_CFLAGS = $(TOOLKIT_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysishumanasm_la_SOURCES:%c=)
