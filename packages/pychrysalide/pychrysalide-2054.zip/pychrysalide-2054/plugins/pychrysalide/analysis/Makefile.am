
noinst_LTLIBRARIES = libpychrysaanalysis.la

libpychrysaanalysis_la_SOURCES =			\
	binary.h binary.c						\
	block.h block.c							\
	cattribs.h cattribs.c					\
	constants.h constants.c					\
	content.h content.c						\
	loaded.h loaded.c						\
	loading.h loading.c						\
	module.h module.c						\
	project.h project.c						\
	routine.h routine.c						\
	type.h type.c							\
	variable.h variable.c

libpychrysaanalysis_la_LIBADD =				\
	contents/libpychrysaanalysiscontents.la	\
	db/libpychrysaanalysisdb.la				\
	disass/libpychrysaanalysisdisass.la		\
	scan/libpychrysaanalysisscan.la			\
	storage/libpychrysaanalysisstorage.la	\
	types/libpychrysaanalysistypes.la

libpychrysaanalysis_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaanalysis_la_SOURCES:%c=)


SUBDIRS = contents db disass scan storage types
