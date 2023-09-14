
# Initialement, ce Makefile est conçu sans définition de am__depfiles_maybe.
# Est-ce parce que GENERATED_FILES est vide et qu'il n'y a donc pas de code
# source ? En tout cas, au premier écrasement de gencode.mk, tous les fichiers
# sont regénérés, et am__depfiles_maybe apparaît enfin. Mais trop tard :
# des fichiers .Plo sont attendus mais non créés par l'ancien Makefile.
# On force les choses ici.
am__depfiles_maybe = depfiles

include gencode.mk

noinst_LTLIBRARIES = libarmv7opcodes.la

libarmv7opcodes_la_SOURCES = $(GENERATED_FILES)

libarmv7opcodes_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) -I$(top_srcdir)/src


devdir = $(includedir)/chrysalide/$(subdir)

dev_HEADERS = $(libarmv7opcodes_la_SOURCES:%c=)


CLEANFILES = $(GENERATED_FILES)

dist-hook:
	cd $(distdir) && rm -f $(CLEANFILES)


EXTRA_DIST = opcodes_tmp_arm.h opcodes_tmp_thumb_16.h opcodes_tmp_thumb_32.h
