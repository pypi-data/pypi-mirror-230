
BUILT_SOURCES = grammar.h


# On évite d'utiliser les variables personnalisées de type *_la_[YL]FLAGS
# afin de conserver des noms de fichiers simples, ie sans le nom de la
# bibliothèque de sortie en préfixe.

AM_YFLAGS = -v -d -p kaitai_ -Wno-yacc -Wcounterexamples

AM_LFLAGS = -P kaitai_ -o lex.yy.c --header-file=tokens.h    		\
                        -Dyyget_lineno=kaitai_get_lineno			\
                        -Dyy_scan_bytes=kaitai__scan_bytes			\
                        -Dyy_delete_buffer=kaitai__delete_buffer

lib_LTLIBRARIES = libkaitai.la

libdir = $(pluginslibdir)


if BUILD_PYTHON_PACKAGE

RUN_PATH = -Wl,-rpath,'$$ORIGIN/../chrysalide-libs'

endif

if BUILD_PYTHON3_BINDINGS

PYTHON3_LIBADD = python/libkaitaipython.la

if BUILD_DISCARD_LOCAL

if BUILD_PYTHON_PACKAGE
PYTHON3_RUN_PATH = -Wl,-rpath,'$$ORIGIN/..'
else
PYTHON3_RUN_PATH = -Wl,-rpath,'$$ORIGIN'
endif

else

PYTHON3_RUN_PATH = -Wl,-rpath,$(abs_top_srcdir)/plugins/pychrysalide/.libs

endif

PYTHON3_LDFLAGS = $(PYTHON3_RUN_PATH) -L$(top_srcdir)/plugins/pychrysalide/.libs -l:pychrysalide.so

PYTHON3_SUBDIRS = python

endif


libkaitai_la_SOURCES =						\
	array-int.h								\
	array.h array.c							\
	core.h core.c							\
	expression.h							\
	parser-int.h							\
	parser.h parser.c						\
	record-int.h							\
	record.h record.c						\
	scope.h scope.c							\
	stream-int.h							\
	stream.h stream.c						\
	tokens.l								\
	grammar.y

libkaitai_la_LIBADD =						\
	parsers/libkaitaiparsers.la				\
	records/libkaitairecords.la				\
	$(PYTHON3_LIBADD)

libkaitai_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src

libkaitai_la_LDFLAGS =						\
	-L$(top_srcdir)/src/.libs -lchrysacore	\
	$(PYTHON3_LDFLAGS)


devdir = $(includedir)/chrysalide-$(subdir)

dev_HEADERS = $(libkaitai_la_SOURCES:%c=)


# Automake fait les choses à moitié
CLEANFILES = grammar.h grammar.c grammar.output tokens.c tokens.h

# Pareil : de tous les fichiers générés, seule la sortie de Flex saute pour les distributions !
EXTRA_DIST = tokens.h


# misc
SUBDIRS = parsers records $(PYTHON3_SUBDIRS)
