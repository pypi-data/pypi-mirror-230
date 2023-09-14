
BUILT_SOURCES = chrysamarshal.h chrysamarshal.c

noinst_LTLIBRARIES  = libglibext.la

libglibext_la_SOURCES =						\
	buffercache-int.h						\
	buffercache.h buffercache.c				\
	bufferline.h bufferline.c				\
	chrysamarshal.h chrysamarshal.c			\
	comparison-int.h						\
	comparison.h comparison.c				\
	configuration-int.h						\
	configuration.h configuration.c			\
	delayed-int.h							\
	delayed.h delayed.c						\
	gbinarycursor.h gbinarycursor.c			\
	gbinportion-int.h						\
	gbinportion.h gbinportion.c				\
	gdisplayoptions.h gdisplayoptions.c		\
	glinecursor-int.h						\
	glinecursor.h glinecursor.c				\
	gnhash.h gnhash.c						\
	linecolumn.h linecolumn.c				\
	linegen-int.h							\
	linegen.h linegen.c						\
	notifier.h								\
	objhole.h								\
	proto.h									\
	seq.h seq.c								\
	signal.h signal.c						\
	singleton.h singleton.c					\
	linesegment.h linesegment.c

if BUILD_GTK_SUPPORT

libglibext_la_SOURCES +=					\
	bufferview.h bufferview.c				\
	gloadedpanel-int.h						\
	gloadedpanel.h gloadedpanel.c			\
	named-int.h								\
	named.h named.c							\
	widthtracker.h widthtracker.c

endif

libglibext_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)

libglibext_la_LIBADD = 					\
	generators/libglibextgenerators.la


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libglibext_la_SOURCES:%c=)


SUBDIRS = generators


chrysamarshal.h: chrysamarshal.list
	glib-genmarshal --header $< > $@

chrysamarshal.c: chrysamarshal.list
	echo "#include <$(subst .c,.h,$@)>" > $@
	glib-genmarshal --body $< >> $@
