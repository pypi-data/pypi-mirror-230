
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin.h - prototypes pour les interactions avec un greffon donné
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_PLUGIN_H
#define _PLUGINS_PLUGIN_H


#include <glib-object.h>


#include "plugin-def.h"
#include "../analysis/binary.h"
#include "../core/logs.h"
#include "../format/format.h"
#include "../format/known.h"
#include "../format/preload.h"
#include "../glibext/configuration.h"
#include "../glibext/notifier.h"
#ifdef INCLUDE_GTK_SUPPORT
#include "../gui/panel.h"
#endif



/* Greffon pour Chrysalide (instance) */
typedef struct _GPluginModule GPluginModule;

/* Greffon pour Chrysalide (classe) */
typedef struct _GPluginModuleClass GPluginModuleClass;


/* Fanions indiquant le statut du greffon */
typedef enum _PluginStatusFlags
{
    PSF_NONE        = (0 << 0),             /* Aucune indication           */
    PSF_UNKNOW_DEP  = (1 << 0),             /* Dépendance non trouvée      */
    PSF_DEP_LOOP    = (1 << 1),             /* Dépendances circulaires     */
    PSF_FAILURE     = (1 << 2),             /* Erreur au chargement        */
    PSF_LOADED      = (1 << 3)              /* Greffon intégré au système  */

} PluginStatusFlags;


#define BROKEN_PLUGIN_STATUS (PSF_UNKNOW_DEP | PSF_DEP_LOOP | PSF_FAILURE)


#define G_TYPE_PLUGIN_MODULE            (g_plugin_module_get_type())
#define G_PLUGIN_MODULE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PLUGIN_MODULE, GPluginModule))
#define G_IS_PLUGIN_MODULE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PLUGIN_MODULE))
#define G_PLUGIN_MODULE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PLUGIN_MODULE, GPluginModuleClass))
#define G_IS_PLUGIN_MODULE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PLUGIN_MODULE))
#define G_PLUGIN_MODULE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PLUGIN_MODULE, GPluginModuleClass))


/* Indique le type défini pour un greffon. */
GType g_plugin_module_get_type(void);

/* Crée un module pour un greffon donné. */
GPluginModule *g_plugin_module_new(const gchar *);

/* Fournit le nom brut associé au greffon. */
char *g_plugin_module_get_modname(const GPluginModule *);

/* Indique le fichier contenant le greffon manipulé. */
const char *g_plugin_module_get_filename(const GPluginModule *);

/* Fournit la description du greffon dans son intégralité. */
const plugin_interface *g_plugin_module_get_interface(const GPluginModule *);

/* Fournit des indications sur l'état du greffon. */
PluginStatusFlags g_plugin_module_get_flags(const GPluginModule *);

/* Ajoute des indications sur l'état du greffon. */
void g_plugin_module_override_flags(GPluginModule *, PluginStatusFlags);

/* Met à jour l'ensemble des dépendances du greffon. */
bool g_plugin_module_resolve_dependencies(GPluginModule *, GPluginModule **, size_t);

/* Termine le chargement du greffon préparé. */
bool g_plugin_module_load(GPluginModule *, GPluginModule **, size_t);

/* Construit le nom d'un fichier de configuration du greffon. */
char *g_plugin_module_build_config_filename(const GPluginModule *, const char *, bool);

/* Fournit la configuration mise en place pour le greffon. */
GGenConfig *g_plugin_module_get_config(const GPluginModule *);

/* Présente dans le journal un message simple. */
void g_plugin_module_log_simple_message(const GPluginModule *, LogMessageType, const char *);

/* Présente dans le journal un message complexe. */
void g_plugin_module_log_variadic_message(const GPluginModule *, LogMessageType, const char *, ...);

/* Encadre une étape de la vie d'un greffon. */
bool g_plugin_module_manage(GPluginModule *, PluginAction);

/* Accompagne la fin du chargement des modules natifs. */
void g_plugin_module_notify_plugins_loaded(GPluginModule *, PluginAction, void *);

/* Crée une instance à partir d'un type dynamique externe. */
gpointer g_plugin_module_build_type_instance(GPluginModule *, PluginAction, GType);

#ifdef INCLUDE_GTK_SUPPORT

/* Complète une liste de resources pour thème. */
void g_plugin_module_include_theme(const GPluginModule *, PluginAction, gboolean, char ***, size_t *);

/* Rend compte de la création d'un panneau. */
void g_plugin_module_notify_panel_creation(const GPluginModule *, PluginAction, GPanelItem *);

/* Rend compte d'un affichage ou d'un retrait de panneau. */
void g_plugin_module_notify_panel_docking(const GPluginModule *, PluginAction, GPanelItem *, bool);

#endif

/* Procède à une opération liée à un contenu binaire. */
void g_plugin_module_handle_binary_content(const GPluginModule *, PluginAction, GBinContent *, wgroup_id_t, GtkStatusStack *);

/* Procède à une opération liée à un contenu chargé. */
void g_plugin_module_handle_loaded_content(const GPluginModule *, PluginAction, GLoadedContent *, wgroup_id_t, GtkStatusStack *);

/* Procède à une opération liée à l'analyse d'un format. */
bool g_plugin_module_handle_known_format_analysis(const GPluginModule *, PluginAction, GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Procède à un préchargement de format de fichier. */
bool g_plugin_module_preload_binary_format(const GPluginModule *, PluginAction, GBinFormat *, GPreloadInfo *, GtkStatusStack *);

/* Procède au rattachement d'éventuelles infos de débogage. */
void g_plugin_module_attach_debug_format(const GPluginModule *, PluginAction, GExeFormat *);

/* Exécute une action pendant un désassemblage de binaire. */
void g_plugin_module_process_disassembly_event(const GPluginModule *, PluginAction, GLoadedBinary *, GtkStatusStack *, GProcContext *);

/* Effectue la détection d'effets d'outils externes. */
void g_plugin_module_detect_external_tools(const GPluginModule *, PluginAction, const GLoadedContent *, bool, char ***, size_t *);



#endif  /* _PLUGINS_PLUGIN_H */
