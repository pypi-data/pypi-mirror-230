
lib_LTLIBRARIES = libchrysacore.la

bin_PROGRAMS = chrysalide chrysalide-hub rost


AM_CPPFLAGS = -I$(top_srcdir) -I$(top_srcdir)/intl



############################################################
# Bibliothèque dynamique
############################################################

#--- libchrysacore

if TRACK_GOBJECT_LEAKS

GOBJECT_LEAKS_SOURCES = gleak.h gleak.c

endif

libchrysacore_la_SOURCES =

if BUILD_GTK_SUPPORT

GTKEXT_LIBADD =								\
	gtkext/libgtkext.la

GTKEXT_SUBDIR = 							\
	gtkext

GUI_LIBADD =								\
	gui/libgui.la

GUI_SUBDIR =								\
	gui

endif


libchrysacore_la_LIBADD =					\
	analysis/libanalysis.la					\
	arch/libarch.la							\
	common/libcommon.la						\
	core/libcore.la							\
	debug/libdebug.la						\
	format/libformat.la						\
	glibext/libglibext.la					\
	$(GTKEXT_LIBADD)						\
	$(GUI_LIBADD)							\
	mangling/libmangling.la					\
	plugins/libplugins.la


# -ldl: dladdr(), dlerror()
libchrysacore_la_LDFLAGS =					\
	-avoid-version -ldl						\
	$(TOOLKIT_LIBS) $(LIBXML_LIBS)			\
	$(LIBSQLITE_LIBS) $(LIBARCHIVE_LIBS)	\
	$(LIBSSL_LIBS)

if BUILD_CURL_SUPPORT

libchrysacore_la_LDFLAGS += $(LIBCURL_LIBS)

endif

if BUILD_MAGIC_SUPPORT

libchrysacore_la_LDFLAGS += $(LIBMAGIC_LIBS)

endif



############################################################
# Programme principal
############################################################

EXTRA_chrysalide_DEPENDENCIES = libchrysacore.la

chrysalide_SOURCES = 					\
	$(GOBJECT_LEAKS_SOURCES)			\
	main.c


chrysalide_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS) $(LIBPYTHON_CFLAGS)

chrysalide_LDFLAGS = $(TOOLKIT_LIBS) -L/usr/X11R6/lib -ldl -lm $(LIBXML_LIBS) $(LIBPYTHON_LIBS) $(LIBARCHIVE_LIBS) $(LIBSQLITE_LIBS) \
	-L.libs -lchrysacore

chrysalide_LDADD = $(LIBINTL)



############################################################
# Gestionnaire de serveurs distants
############################################################

EXTRA_chrysalide_hub_DEPENDENCIES = libchrysacore.la

chrysalide_hub_SOURCES =				\
	$(GOBJECT_LEAKS_SOURCES)			\
	hub.c

chrysalide_hub_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)

chrysalide_hub_LDFLAGS = $(TOOLKIT_LIBS) $(LIBXML_LIBS) -L.libs -lchrysacore



############################################################
# Détecteur de motifs
############################################################

EXTRA_rost_DEPENDENCIES = libchrysacore.la

rost_SOURCES =							\
	$(GOBJECT_LEAKS_SOURCES)			\
	rost.c

rost_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)

rost_LDFLAGS = $(LIBGOBJ_LIBS) -L.libs -lchrysacore



############################################################
# Le reste du monde
############################################################

# glibext doit être traité en premier, à cause des marshals GLib

SUBDIRS = core glibext $(GTKEXT_SUBDIR) analysis arch format common debug $(GUI_SUBDIR) mangling plugins
