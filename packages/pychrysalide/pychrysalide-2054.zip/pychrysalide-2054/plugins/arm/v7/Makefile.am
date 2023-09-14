
noinst_LTLIBRARIES = libarmv7.la

libarmv7_la_SOURCES =						\
	arm.h arm.c								\
	context.h context.c						\
	core.h core.c							\
	fetch.h fetch.c							\
	helpers.h								\
	instruction.h instruction.c				\
	link.h link.c							\
	operand-int.h							\
	operand.h operand.c						\
	post.h post.c							\
	processor.h processor.c					\
	pseudo.h pseudo.c						\
	register-int.h							\
	register.h register.c					\
	thumb_16.h thumb_16.c					\
	thumb_32.h thumb_32.c

libarmv7_la_LIBADD =						\
	opcodes/libarmv7opcodes.la				\
	operands/libarmv7operands.la			\
	registers/libarmv7registers.la

libarmv7_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libarmv7_la_SOURCES:%c=)


SUBDIRS = opdefs opcodes operands registers
