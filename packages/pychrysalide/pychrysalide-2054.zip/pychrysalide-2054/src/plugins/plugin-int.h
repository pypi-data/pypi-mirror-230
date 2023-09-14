
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin-int.h - prototypes pour les structures internes des greffons
 *
 * Copyright (C) 2010-2019 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _PLUGINS_PLUGIN_INT_H
#define _PLUGINS_PLUGIN_INT_H


#include <glib-object.h>
#include <stdbool.h>


#include "plugin.h"
#include "../analysis/content.h"
#include "../analysis/loaded.h"
#include "../common/bits.h"



/* Transfert de la conscience de soi. */
typedef void (* pg_set_self_fc) (GPluginModule *);

/* Prend acte du [dé]chargement du greffon. */
typedef bool (* pg_management_fc) (GPluginModule *);

/* Accompagne la fin du chargement des modules natifs. */
typedef void (* pg_plugins_loaded_fc) (GPluginModule *, PluginAction);

/* Crée une instance à partir d'un type dynamique externe. */
typedef gpointer (* pg_build_instance_fc) (GPluginModule *, PluginAction, GType);

/* Fournit le nom brut associé au greffon. */
typedef char * (* pg_get_modname_fc) (const GPluginModule *);

/* Procède à une opération liée à un contenu binaire. */
typedef void (* pg_handle_content_fc) (const GPluginModule *, PluginAction, GBinContent *, wgroup_id_t, GtkStatusStack *);

/* Procède à une opération liée à un contenu chargé. */
typedef void (* pg_handle_loaded_fc) (const GPluginModule *, PluginAction, GLoadedContent *, wgroup_id_t, GtkStatusStack *);

#ifdef INCLUDE_GTK_SUPPORT

/* Complète une liste de resources pour thème. */
typedef void (* pg_include_theme_fc) (const GPluginModule *, PluginAction, gboolean, char ***, size_t *);

/* Rend compte de la création d'un panneau. */
typedef void (* pg_notify_panel_fc) (const GPluginModule *, PluginAction, GPanelItem *);

/* Rend compte d'un affichage ou d'un retrait de panneau. */
typedef void (* pg_notify_docking_fc) (const GPluginModule *, PluginAction, GPanelItem *, bool);

#endif

/* Assure l'interprétation d'un format en différé. */
typedef bool (* pg_handle_format_analysis_fc) (const GPluginModule *, PluginAction, GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Procède à un préchargement de format de fichier. */
typedef bool (* pg_preload_format_fc) (const GPluginModule *, PluginAction, GBinFormat *, GPreloadInfo *, GtkStatusStack *);

/* Procède au rattachement d'éventuelles infos de débogage. */
typedef void (* pg_attach_debug) (const GPluginModule *, PluginAction, GExeFormat *);

/* Exécute une action pendant un désassemblage de binaire. */
typedef void (* pg_process_disassembly_fc) (const GPluginModule *, PluginAction, GLoadedBinary *, GtkStatusStack *, GProcContext *);

/* Effectue la détection d'effets d'outils externes. */
typedef void (* pg_detect_tools_fc) (const GPluginModule *, PluginAction, const GLoadedContent *, bool, char ***, size_t *);


/* Greffon pour Chrysalide (instance) */
struct _GPluginModule
{
    GObject parent;                         /* A laisser en premier        */

    char *filename;                         /* Fichier associé au greffon  */
    GModule *module;                        /* Abstration de manipulation  */

    const plugin_interface *interface;      /* Déclaration d'interfaçage   */

    PluginStatusFlags flags;                /* Fanion pour l'état courant  */

    bitfield_t *dependencies;               /* Cartographie des dépendances*/

    GGenConfig *config;                     /* Configuration dédiée        */

};


/* Greffon pour Chrysalide (classe) */
struct _GPluginModuleClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    pg_management_fc init;                  /* Procédure d'initialisation  */
    pg_management_fc manage;                /* Etape dans la vie du greffon*/
    pg_management_fc exit;                  /* Procédure d'extinction      */

    pg_plugins_loaded_fc plugins_loaded;    /* Fin des chargements         */
    pg_build_instance_fc build_instance;    /* Création d'objets           */

    pg_get_modname_fc get_modname;          /* Fourniture du nom brut      */

#ifdef INCLUDE_GTK_SUPPORT
    pg_include_theme_fc include_theme;      /* Extension d'un thème        */
    pg_notify_panel_fc notify_panel;        /* Création de panneau         */
    pg_notify_docking_fc notify_docking;    /* Affichage ou retrait        */
#endif

    pg_handle_content_fc handle_content;    /* Explorations ou résolutions */
    pg_handle_loaded_fc handle_loaded;      /* Traitement de contenu chargé*/

    pg_handle_format_analysis_fc handle_fmt_analysis; /* Analyse de format */
    pg_preload_format_fc preload_format;    /* Préchargement d'un format   */
    pg_attach_debug attach_debug;           /* Informations de débogage    */

    pg_process_disassembly_fc process_disass; /* Catégorie 'désassemblage' */

    pg_detect_tools_fc detect;              /* Lancement de détections     */

};


/* Met en place la configuration dédiée au greffon. */
void g_plugin_module_create_config(GPluginModule *);



#endif  /* _PLUGINS_PLUGIN_INT_H */
