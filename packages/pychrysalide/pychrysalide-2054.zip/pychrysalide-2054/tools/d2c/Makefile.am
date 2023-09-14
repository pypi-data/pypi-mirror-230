
BUILT_SOURCES = grammar.h


# On évite d'utiliser les variables personnalisées de type *_la_[YL]FLAGS
# afin de conserver des noms de fichiers simples, ie sans le nom de la
# bibliothèque de sortie en préfixe.

AM_YFLAGS = -v -d -p d2c_ -Wno-yacc

AM_LFLAGS = -P d2c_ -o lex.yy.c --header-file=tokens.h			\
			-Dyyget_lineno=d2c_get_lineno 						\
			-Dyy_scan_bytes=d2c__scan_bytes						\
			-Dyy_delete_buffer=d2c__delete_buffer

AM_CFLAGS = $(DEBUG_CFLAGS) $(WARNING_FLAGS)


bin_PROGRAMS = d2c

.NOTPARALLEL: $(bin_PROGRAMS)

d2c_SOURCES =							\
	coder.h coder.c						\
	d2c.c								\
	decl.h								\
	encoding.h encoding.c				\
	helpers.h helpers.c					\
	manual.h							\
	pproc.h pproc.c						\
	qckcall.h qckcall.c					\
	syntax.h syntax.c					\
	tokens.l							\
	grammar.y

# _GNU_SOURCE : asprintf
d2c_CFLAGS = -D_GNU_SOURCE

d2c_LDADD =								\
	assert/libd2cassert.la				\
	bits/libd2cbits.la					\
	conv/libd2cconv.la					\
	desc/libd2cdesc.la					\
	format/libd2cformat.la				\
	hooks/libd2chooks.la				\
	id/libd2cid.la						\
	pattern/libd2cpattern.la			\
	rules/libd2crules.la				\
	args/libd2cargs.la

d2c_LDFLAGS = -lm


# Automake fait les choses à moitié
CLEANFILES = grammar.h grammar.c grammar.output tokens.c tokens.h

# Pareil : de tous les fichiers générés, seule la sortie de Flex saute pour les distributions !
# On rajoute également de quoi générer les Makefiles.
EXTRA_DIST = tokens.h d2c_genmakefile.sh d2c.mk


SUBDIRS = args assert bits conv desc format hooks id pattern rules
