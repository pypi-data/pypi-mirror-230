
BUILT_SOURCES = grammar.h


# On évite d'utiliser les variables personnalisées de type *_la_[YL]FLAGS
# afin de conserver des noms de fichiers simples, ie sans le nom de la
# bibliothèque de sortie en préfixe.

AM_YFLAGS = -v -d -p args_ -Wno-yacc

AM_LFLAGS = -P args_ -o lex.yy.c --header-file=tokens.h			\
			-Dyyget_lineno=args_get_lineno 						\
			-Dyy_scan_string=args__scan_string					\
			-Dyy_delete_buffer=args__delete_buffer

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS)


noinst_LTLIBRARIES  = libd2cargs.la

.NOTPARALLEL: $(noinst_LTLIBRARIES)

libd2cargs_la_SOURCES =					\
	decl.h								\
	manager.h manager.c					\
	tokens.l							\
	grammar.y

# _GNU_SOURCE : asprintf
libd2cargs_la_CFLAGS = -D_GNU_SOURCE


# Automake fait les choses à moitié
CLEANFILES = grammar.h grammar.c grammar.output tokens.c tokens.h

# Pareil : de tous les fichiers générés, seule la sortie de Flex saute pour les distributions !
EXTRA_DIST = tokens.h
