
noinst_LTLIBRARIES  = libanalysiscontents.la

libanalysiscontents_la_SOURCES =		\
	encapsulated.h encapsulated.c		\
	file.h file.c						\
	memory-int.h						\
	memory.h memory.c					\
	restricted.h restricted.c

libanalysiscontents_la_CFLAGS = $(TOOLKIT_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysiscontents_la_SOURCES:%c=)
