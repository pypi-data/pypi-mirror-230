
BUILT_SOURCES = grammar.h


# On évite d'utiliser les variables personnalisées de type *_la_[YL]FLAGS
# afin de conserver des noms de fichiers simples, ie sans le nom de la
# bibliothèque de sortie en préfixe.

AM_YFLAGS = -v -d -p rost_ -Wno-yacc -Wcounterexamples

AM_LFLAGS = -P rost_ -o lex.yy.c --header-file=tokens.h    		\
                        -Dyyget_lineno=rost_get_lineno          \
                        -Dyy_scan_bytes=rost__scan_bytes        \
                        -Dyy_delete_buffer=rost__delete_buffer

noinst_LTLIBRARIES  = libanalysisscan.la


libanalysisscan_la_SOURCES =				\
	cond-int.h								\
	cond.h cond.c							\
	context-int.h							\
	context.h context.c						\
	core.h core.c							\
	expr-int.h								\
	expr.h expr.c							\
	item-int.h								\
	item.h item.c							\
	match-int.h								\
	match.h match.c							\
	options-int.h							\
	options.h options.c						\
	pattern-int.h							\
	pattern.h pattern.c						\
	rule-int.h								\
	rule.h rule.c							\
	scanner-int.h							\
	scanner.h scanner.c						\
	scope-int.h								\
	scope.h scope.c							\
	space-int.h								\
	space.h space.c							\
	tokens.l								\
	grammar.y

libanalysisscan_la_LIBADD = 				\
	exprs/libanalysisscanexprs.la			\
	items/libanalysisscanitems.la			\
	matches/libanalysisscanmatches.la		\
	patterns/libanalysisscanpatterns.la

libanalysisscan_la_CFLAGS = $(LIBGOBJ_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscan_la_SOURCES:%c=)


# Automake fait les choses à moitié
CLEANFILES = grammar.h grammar.c grammar.output tokens.c tokens.h

# Pareil : de tous les fichiers générés, seule la sortie de Flex saute pour les distributions !
EXTRA_DIST = tokens.h


SUBDIRS = exprs items matches patterns
