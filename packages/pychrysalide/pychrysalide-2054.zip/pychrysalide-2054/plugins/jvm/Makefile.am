
noinst_LTLIBRARIES = libarchjvm.la

libarchjvm_la_SOURCES =					\
	instruction.h instruction.c			\
	op_add.c							\
	op_const.c							\
	op_convert.c						\
	op_dup.c							\
	op_getput.c							\
	op_invoke.c							\
	op_load.c							\
	op_monitor.c						\
	op_nop.c							\
	op_pop.c							\
	op_store.c							\
	op_ret.c							\
	opcodes.h							\
	operand.h operand.c					\
	processor.h processor.c

libarchjvm_la_CFLAGS = $(AM_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=%)

dev_HEADERS = $(libarchjvm_la_SOURCES:%c=)


AM_CPPFLAGS = $(LIBGTK_CFLAGS) $(LIBXML_CFLAGS)

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS) $(COMPLIANCE_FLAGS)


SUBDIRS = 
