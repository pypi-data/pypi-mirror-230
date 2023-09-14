
noinst_LTLIBRARIES = libkaitaiparsers.la

libkaitaiparsers_la_SOURCES =				\
	attribute-int.h							\
	attribute.h attribute.c					\
	enum-int.h								\
	enum.h enum.c							\
	instance-int.h							\
	instance.h instance.c					\
	meta-int.h								\
	meta.h meta.c							\
	struct-int.h							\
	struct.h struct.c						\
	switch-int.h							\
	switch.h switch.c						\
	type-int.h								\
	type.h type.c

libkaitaiparsers_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide-$(subdir)

dev_HEADERS = $(libkaitaiparsers_la_SOURCES:%c=)
