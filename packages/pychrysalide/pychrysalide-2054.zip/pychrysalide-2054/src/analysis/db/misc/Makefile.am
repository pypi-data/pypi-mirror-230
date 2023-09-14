
noinst_LTLIBRARIES  = libanalysisdbmisc.la

libanalysisdbmisc_la_SOURCES =			\
	rlestr.h rlestr.c					\
	snapshot.h snapshot.c				\
	timestamp.h timestamp.c


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisdbmisc_la_SOURCES:%c=)
