
noinst_LTLIBRARIES = libpychrysaanalysistypes.la

libpychrysaanalysistypes_la_SOURCES =		\
	array.h array.c							\
	basic.h basic.c							\
	constants.h constants.c					\
	cse.h cse.c								\
	encaps.h encaps.c						\
	expr.h expr.c							\
	literal.h literal.c						\
	module.h module.c						\
	override.h override.c					\
	proto.h proto.c							\
	template.h template.c

libpychrysaanalysistypes_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysistypes_la_SOURCES:%c=)
