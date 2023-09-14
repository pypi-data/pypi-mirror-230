
BUILT_SOURCES = gram.h

AM_YFLAGS = -d

lib_LTLIBRARIES = libarchgovm.la

bin_PROGRAMS = goas


#--- liboidadisas

libarchgovm_la_SOURCES = 				\
	instruction.h instruction.c

libarchgovm_la_LDFLAGS = 

libarchgovm_la_LIBADD = 


#--- goas

goas_SOURCES =							\
	build.h build.c						\
	goas.c								\
	gram.y								\
	tok.l


AM_CPPFLAGS = 

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS) $(COMPLIANCE_FLAGS)


goas_LDFLAGS = -L.libs

goas_LDADD = $(LIBINTL) -larchgovm


# Automake fait les choses à moitié
CLEANFILES = gram.h gram.c tok.c
