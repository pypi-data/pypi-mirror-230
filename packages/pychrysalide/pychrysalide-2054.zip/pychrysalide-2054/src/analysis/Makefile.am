
noinst_LTLIBRARIES  = libanalysis.la

libanalysis_la_SOURCES =				\
	binary.h binary.c					\
	block-int.h							\
	block.h block.c						\
	cattribs.h cattribs.c				\
	content-int.h						\
	content.h content.c					\
	loaded-int.h						\
	loaded.h loaded.c					\
	loading.h loading.c					\
	project.h project.c					\
	routine-int.h						\
	routine.h routine.c					\
	type-int.h							\
	type.h type.c						\
	variable.h variable.c

libanalysis_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)

libanalysis_la_LIBADD =					\
	contents/libanalysiscontents.la		\
	db/libanalysisdb.la					\
	disass/libanalysisdisass.la			\
	human/libanalysishuman.la			\
	scan/libanalysisscan.la				\
	storage/libanalysisstorage.la		\
	types/libanalysistypes.la


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysis_la_SOURCES:%c=)


SUBDIRS = contents db disass human scan storage types
