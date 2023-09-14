
noinst_LTLIBRARIES  = libanalysistypes.la

libanalysistypes_la_SOURCES =			\
	array.h array.c						\
	basic.h basic.c						\
	cse.h cse.c							\
	encaps.h encaps.c					\
	expr.h expr.c						\
	literal.h literal.c					\
	override.h override.c				\
	proto.h proto.c						\
	template.h template.c

libanalysistypes_la_CFLAGS = $(TOOLKIT_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysistypes_la_SOURCES:%c=)
