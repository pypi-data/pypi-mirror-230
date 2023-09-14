
noinst_LTLIBRARIES = libpychrysaarch.la

libpychrysaarch_la_SOURCES =				\
	constants.h constants.c					\
	context.h context.c						\
	instriter.h instriter.c					\
	instruction.h instruction.c				\
	module.h module.c						\
	operand.h operand.c						\
	processor.h processor.c					\
	register.h register.c					\
	vmpa.h vmpa.c

libpychrysaarch_la_LIBADD =					\
	instructions/libpychrysaarchinstructions.la \
	operands/libpychrysaarchoperands.la

libpychrysaarch_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS) $(LIBPYGOBJECT_CFLAGS) \
	-I$(top_srcdir)/src -DNO_IMPORT_PYGOBJECT


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libpychrysaarch_la_SOURCES:%c=)


SUBDIRS = instructions operands
