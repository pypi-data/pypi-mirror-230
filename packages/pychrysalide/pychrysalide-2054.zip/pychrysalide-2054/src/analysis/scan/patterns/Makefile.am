
noinst_LTLIBRARIES  = libanalysisscanpatterns.la


libanalysisscanpatterns_la_SOURCES =		\
	backend-int.h							\
	backend.h backend.c						\
	modifier-int.h							\
	modifier.h modifier.c					\
	token-int.h								\
	token.h token.c

libanalysisscanpatterns_la_LIBADD = 		\
	backends/libanalysisscanpatternsbackends.la \
	modifiers/libanalysisscanpatternsmodifiers.la \
	tokens/libanalysisscanpatternstokens.la

libanalysisscanpatterns_la_CFLAGS = $(LIBGOBJ_CFLAGS) $(LIBPYTHON_INTERPRETER_CFLAGS)


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanpatterns_la_SOURCES:%c=)


SUBDIRS = backends modifiers tokens
