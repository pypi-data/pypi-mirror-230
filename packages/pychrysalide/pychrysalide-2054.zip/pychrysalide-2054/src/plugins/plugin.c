
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin.c - interactions avec un greffon donné
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


#include "plugin.h"


#include <assert.h>
#include <gmodule.h>
#include <libgen.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>


#include "dt.h"
#include "pglist.h"
#include "plugin-int.h"
#include "../common/extstr.h"
#include "../common/pathname.h"
#include "../common/xdg.h"



/* Initialise la classe des greffons. */
static void g_plugin_module_class_init(GPluginModuleClass *);

/* Initialise une instance de greffon. */
static void g_plugin_module_init(GPluginModule *);

/* Supprime toutes les références externes. */
static void g_plugin_module_dispose(GPluginModule *);

/* Procède à la libération totale de la mémoire. */
static void g_plugin_module_finalize(GPluginModule *);

/* Initialise la classe des greffons d'extension. */
static void g_plugin_module_init_gclass(GPluginModuleClass *, GModule *);

/* Fournit le nom brut associé au greffon. */
static char *_g_plugin_module_get_modname(const GPluginModule *);



/* Indique le type défini pour un greffon. */
G_DEFINE_TYPE(GPluginModule, g_plugin_module, G_TYPE_OBJECT);



/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des greffons.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_module_class_init(GPluginModuleClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GPluginModuleClass *plugin;             /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_plugin_module_dispose;
    object->finalize = (GObjectFinalizeFunc)g_plugin_module_finalize;

    plugin = G_PLUGIN_MODULE_CLASS(class);

    plugin->get_modname = (pg_get_modname_fc)_g_plugin_module_get_modname;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de greffon.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_module_init(GPluginModule *plugin)
{
    plugin->config = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_module_dispose(GPluginModule *plugin)
{
    const plugin_interface *pg_iface;       /* Définition du greffon       */
    size_t i;                               /* Boucle de parcours          */
    GPluginModule *dependency;              /* Module nécessaire           */
    GPluginModuleClass *class;              /* Classe de l'instance active */

    pg_iface = g_plugin_module_get_interface(plugin);

    if (pg_iface != NULL)
    {
        lock_plugin_list_for_reading();

        for (i = 0; i < pg_iface->required_count; i++)
        {
            dependency = get_plugin_by_name(pg_iface->required[i], NULL);

            /* Si le chargement a bien été complet avant la sortie... */
            if (dependency != NULL)
            {
                /* Un coup pour l'appel à get_plugin_by_name(). */
                g_object_unref(G_OBJECT(dependency));

                /* Un coup pour la dépendance */
                g_object_unref(G_OBJECT(dependency));

            }

        }

        unlock_plugin_list_for_reading();

    }

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    if (class->exit != NULL)
        class->exit(plugin);

    if (plugin->config != NULL)
    {
        g_generic_config_write(plugin->config);

        g_clear_object(&plugin->config);

    }

    if (plugin->module != NULL)
    {
        g_module_close(plugin->module);
        plugin->module = NULL;
    }

    G_OBJECT_CLASS(g_plugin_module_parent_class)->dispose(G_OBJECT(plugin));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_module_finalize(GPluginModule *plugin)
{
    free(plugin->filename);

    if (plugin->dependencies != NULL)
        delete_bit_field(plugin->dependencies);

    G_OBJECT_CLASS(g_plugin_module_parent_class)->finalize(G_OBJECT(plugin));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = nom du fichier à charger.                         *
*                                                                             *
*  Description : Crée un module pour un greffon donné.                        *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPluginModule *g_plugin_module_new(const gchar *filename)
{
    GPluginModule *result;                  /* Structure à retourner       */
    GModule *module;                        /* Abstration de manipulation  */
    pg_set_self_fc set_self;                /* Copie du greffon            */
    const plugin_interface *interface;      /* Déclaration d'interfaçage   */
    plugin_abi_version_t current;           /* Version de l'ABI actuelle   */
    bool valid;                             /* Statut de validité          */
    size_t i;                               /* Boucle de parcours          */
    uint32_t action;                        /* Identifiant d'une action    */
    uint32_t category;                      /* Catégorie principale        */
    uint32_t sub;                           /* Sous-catégorie visée        */
    GType gtype;                            /* Nouveau type de greffon     */

    module = g_module_open(filename, G_MODULE_BIND_LAZY);
    if (module == NULL)
    {
        log_variadic_message(LMT_ERROR, 
                             _("Error while loading the plugin candidate '%s' : %s"),
                             filename, g_module_error());
        goto bad_module;
    }


#define load_plugin_symbol(mod, sym, dest)                                          \
    ({                                                                              \
        bool __result;                                                              \
        if (!g_module_symbol(mod, sym, (gpointer *)dest))                           \
        {                                                                           \
            log_variadic_message(LMT_ERROR,                                         \
                                 _("No '%s' entry in plugin candidate '%s'"),       \
                                 sym, filename);                                    \
            __result = false;                                                       \
        }                                                                           \
        else __result = true;                                                       \
        __result;                                                                   \
    })


    /* Récupération de la version d'ABI */

    if (!load_plugin_symbol(module, "chrysalide_plugin_set_self", &set_self))
        goto no_self_setter;

    if (!load_plugin_symbol(module, "_chrysalide_plugin", &interface))
        goto no_interface;

    current = CURRENT_ABI_VERSION;

    if (current != interface->abi_version)
        goto wrong_abi;

    /* Localisation des différents points d'entrée déclarés */


#define check_plugin_symbol(mod, sym)                                           \
    ({                                                                          \
        bool __result;                                                          \
        __result = g_module_symbol(mod, sym, (gpointer []) { NULL });           \
        if (!__result)                                                          \
            log_variadic_message(LMT_ERROR,                                     \
                                 _("No '%s' entry in plugin candidate '%s'"),   \
                                 sym, filename);                                \
        __result;                                                               \
    })


    valid = true;

    for (i = 0; i < interface->actions_count && valid; i++)
    {
        action = interface->actions[i];
        category = MASK_PLUGIN_CATEGORY(action);
        sub = MASK_PLUGIN_SUB_CATEGORY(action);

        switch (category)
        {
            case DPC_BASIC:

                switch (sub)
                {
                    case DPS_NONE:
                        break;

                    case DPS_PG_MANAGEMENT:

                        switch (action)
                        {
                            case PGA_PLUGIN_INIT:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_init");
                                break;

                            case PGA_PLUGIN_LOADED:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_manage");
                                break;

                            case PGA_PLUGIN_EXIT:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_exit");
                                break;

                            default:
                                log_variadic_message(LMT_WARNING,
                                                     _("Unknown action '0x%02x' in plugin '%s'..."),
                                                     interface->actions[i], filename);
                                break;

                        }

                        break;

                    case DPS_CORE_MANAGEMENT:

                        switch (action)
                        {
                            case PGA_NATIVE_PLUGINS_LOADED:
                            case PGA_ALL_PLUGINS_LOADED:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_on_plugins_loaded");
                                break;

                            case PGA_TYPE_BUILDING:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_build_type_instance");
                                break;

                            default:
                                log_variadic_message(LMT_WARNING,
                                                     _("Unknown action '0x%02x' in plugin '%s'..."),
                                                     interface->actions[i], filename);
                                break;

                        }

                        break;

                    default:
                        log_variadic_message(LMT_WARNING,
                                             _("Unknown sub-category '0x%02x' in plugin '%s'..."), sub, filename);
                        break;

                }

                break;

            case DPC_GUI:

                switch (sub)
                {
                    case DPS_SETUP:

                        switch (action)
                        {
                            case PGA_GUI_THEME:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_include_theme");
                                break;

                            default:
                                log_variadic_message(LMT_WARNING,
                                                     _("Unknown action '0x%02x' in plugin '%s'..."),
                                                     interface->actions[i], filename);
                                break;

                        }

                        break;

                    case DPS_RUNNING:

                        switch (action)
                        {
                            case PGA_PANEL_CREATION:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_on_panel_creation");
                                break;

                            case PGA_PANEL_DOCKING:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_on_panel_docking");
                                break;

                            default:
                                log_variadic_message(LMT_WARNING,
                                                     _("Unknown action '0x%02x' in plugin '%s'..."),
                                                     interface->actions[i], filename);
                                break;

                        }

                        break;

                    default:
                        log_variadic_message(LMT_WARNING,
                                             _("Unknown sub-category '0x%02x' in plugin '%s'..."), sub, filename);
                        break;

                }

                break;

            case DPC_BINARY_PROCESSING:

                switch (sub)
                {
                    case DPS_CONTENT:

                        switch (action)
                        {
                            case PGA_CONTENT_EXPLORER:
                            case PGA_CONTENT_RESOLVER:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_handle_binary_content");
                                break;

                            case PGA_CONTENT_ANALYZED:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_handle_loaded_content");
                                break;

                            default:
                                log_variadic_message(LMT_WARNING,
                                                     _("Unknown action '0x%02x' in plugin '%s'..."),
                                                     interface->actions[i], filename);
                                break;

                        }

                        break;

                    case DPS_FORMAT:

                        switch (action)
                        {
                            case PGA_FORMAT_ANALYSIS_STARTED:
                            case PGA_FORMAT_ANALYSIS_ENDED:
                            case PGA_FORMAT_POST_ANALYSIS_STARTED:
                            case PGA_FORMAT_POST_ANALYSIS_ENDED:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_handle_binary_format_analysis");
                                break;

                            case PGA_FORMAT_PRELOAD:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_preload_binary_format");
                                break;

                            case PGA_FORMAT_ATTACH_DEBUG:
                                valid = check_plugin_symbol(module, "chrysalide_plugin_attach_debug");
                                break;

                            default:
                                log_variadic_message(LMT_WARNING,
                                                     _("Unknown action '0x%02x' in plugin '%s'..."),
                                                     interface->actions[i], filename);
                                break;

                        }

                        break;

                    case DPS_DISASSEMBLY:
                        valid = check_plugin_symbol(module, "chrysalide_plugin_process_disassembly_event");
                        break;

                    case DPS_DETECTION:
                        valid = check_plugin_symbol(module, "chrysalide_plugin_detect_external_tools");
                        break;

                    default:
                        log_variadic_message(LMT_WARNING,
                                             _("Unknown sub-category '0x%02x' in plugin '%s'..."), sub, filename);
                        break;

                }

                break;

            default:
                log_variadic_message(LMT_WARNING,
                                     _("Unknown category '0x%02x' in plugin '%s'..."), category, filename);
                break;

        }

    }

    if (!valid)
        goto missing_feature;

    gtype = build_dynamic_type(G_TYPE_PLUGIN_MODULE, interface->gtp_name,
                               (GClassInitFunc)g_plugin_module_init_gclass, module, NULL);

    if (gtype == G_TYPE_INVALID)
        goto no_instance;

    result = g_object_new(gtype, NULL);

    result->filename = strdup(filename);
    result->module = module;

    result->interface = interface;

    set_self(result);

    return result;

 no_self_setter:

    log_variadic_message(LMT_ERROR, _("Self pointer setter is missing for plugin '%s'"), filename);
    goto bad_plugin;

 no_interface:

    log_variadic_message(LMT_ERROR, _("Main interface is missing for plugin '%s'"), filename);
    goto bad_plugin;

 wrong_abi:

    log_variadic_message(LMT_ERROR, _("ABI mismatch detected! Plugin '%s' rejected"), filename);
    goto bad_plugin;

 missing_feature:

    log_variadic_message(LMT_ERROR, _("An expected feature is missing for plugin '%s'"), filename);
    goto bad_plugin;

 no_instance:

    log_variadic_message(LMT_ERROR, _("Unabled to create an instance of plugin '%s'"), filename);

 bad_plugin:

    g_module_close(module);

 bad_module:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                module = module représentant le greffon chargé en mémoire.   *
*                                                                             *
*  Description : Initialise la classe des greffons d'extension.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_module_init_gclass(GPluginModuleClass *class, GModule *module)
{
    const plugin_interface *interface;      /* Déclaration d'interfaçage   */
    size_t i;                               /* Boucle de parcours          */
    uint32_t action;                        /* Identifiant d'une action    */
    uint32_t category;                      /* Catégorie principale        */
    uint32_t sub;                           /* Sous-catégorie visée        */


#undef load_plugin_symbol

#define load_plugin_symbol(mod, sym, dest)                          \
    ({                                                              \
        bool __result;                                              \
        __result = g_module_symbol(mod, sym, (gpointer *)dest);     \
        assert(__result);                                           \
        __result;                                                   \
    })


    load_plugin_symbol(module, "_chrysalide_plugin", &interface);

    for (i = 0; i < interface->actions_count; i++)
    {
        action = interface->actions[i];
        category = MASK_PLUGIN_CATEGORY(action);
        sub = MASK_PLUGIN_SUB_CATEGORY(action);

        switch (category)
        {
            case DPC_BASIC:

                switch (sub)
                {
                    case DPS_NONE:
                        break;

                    case DPS_PG_MANAGEMENT:

                        switch (action)
                        {
                            case PGA_PLUGIN_INIT:
                                load_plugin_symbol(module, "chrysalide_plugin_init", &class->init);
                                break;

                            case PGA_PLUGIN_LOADED:
                                load_plugin_symbol(module, "chrysalide_plugin_manage", &class->manage);
                                break;

                            case PGA_PLUGIN_EXIT:
                                load_plugin_symbol(module, "chrysalide_plugin_exit", &class->exit);
                                break;

                            default:
                                assert(false);
                                break;

                        }

                        break;

                    case DPS_CORE_MANAGEMENT:

                        switch (action)
                        {
                            case PGA_NATIVE_PLUGINS_LOADED:
                            case PGA_ALL_PLUGINS_LOADED:
                                load_plugin_symbol(module, "chrysalide_plugin_on_plugins_loaded",
                                                   &class->plugins_loaded);
                                break;

                            case PGA_TYPE_BUILDING:
                                load_plugin_symbol(module, "chrysalide_plugin_build_type_instance",
                                                   &class->build_instance);
                                break;

                            default:
                                assert(false);
                                break;

                        }

                        break;

                    default:
                        assert(false);
                        break;

                }

                break;

            case DPC_GUI:

                switch (sub)
                {
                    case DPS_SETUP:

                        switch (action)
                        {
                            case PGA_GUI_THEME:
#ifdef INCLUDE_GTK_SUPPORT
                                load_plugin_symbol(module, "chrysalide_plugin_include_theme",
                                                   &class->include_theme);
#endif
                                break;

                            default:
                                assert(false);
                                break;

                        }

                        break;

                    case DPS_RUNNING:

                        switch (action)
                        {
                            case PGA_PANEL_CREATION:
#ifdef INCLUDE_GTK_SUPPORT
                                load_plugin_symbol(module, "chrysalide_plugin_on_panel_creation",
                                                   &class->notify_panel);
#endif
                                break;

                            case PGA_PANEL_DOCKING:
#ifdef INCLUDE_GTK_SUPPORT
                                load_plugin_symbol(module, "chrysalide_plugin_on_panel_docking",
                                                   &class->notify_docking);
#endif
                                break;

                            default:
                                assert(false);
                                break;

                        }

                        break;

                    default:
                        assert(false);
                        break;

                }

                break;

            case DPC_BINARY_PROCESSING:

                switch (sub)
                {
                    case DPS_CONTENT:

                        switch (action)
                        {
                            case PGA_CONTENT_EXPLORER:
                            case PGA_CONTENT_RESOLVER:
                                load_plugin_symbol(module, "chrysalide_plugin_handle_binary_content",
                                                   &class->handle_content);
                                break;

                            case PGA_CONTENT_ANALYZED:
                                load_plugin_symbol(module, "chrysalide_plugin_handle_loaded_content",
                                                   &class->handle_loaded);
                                break;

                            default:
                                assert(false);
                                break;

                        }

                        break;

                    case DPS_FORMAT:

                        switch (action)
                        {
                            case PGA_FORMAT_ANALYSIS_STARTED:
                            case PGA_FORMAT_ANALYSIS_ENDED:
                            case PGA_FORMAT_POST_ANALYSIS_STARTED:
                            case PGA_FORMAT_POST_ANALYSIS_ENDED:
                                load_plugin_symbol(module, "chrysalide_plugin_handle_binary_format_analysis",
                                                   &class->handle_fmt_analysis);
                                break;

                            case PGA_FORMAT_PRELOAD:
                                load_plugin_symbol(module, "chrysalide_plugin_preload_binary_format", &class->preload_format);
                                break;

                            case PGA_FORMAT_ATTACH_DEBUG:
                                load_plugin_symbol(module, "chrysalide_plugin_attach_debug", &class->attach_debug);
                                break;

                            default:
                                assert(false);
                                break;

                        }

                        break;

                    case DPS_DISASSEMBLY:
                        load_plugin_symbol(module, "chrysalide_plugin_process_disassembly_event", &class->process_disass);
                        break;

                    case DPS_DETECTION:
                        load_plugin_symbol(module, "chrysalide_plugin_detect_external_tools", &class->detect);
                        break;

                    default:
                        assert(false);
                        break;

                }

                break;

            default:
                assert(false);
                break;

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à valider.                                  *
*                                                                             *
*  Description : Fournit le nom brut associé au greffon.                      *
*                                                                             *
*  Retour      : Désignation brute du greffon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_plugin_module_get_modname(const GPluginModule *plugin)
{
    char *result;                           /* Désignation brute à renvoyer*/
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    result = class->get_modname(plugin);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à valider.                                  *
*                                                                             *
*  Description : Fournit le nom brut associé au greffon.                      *
*                                                                             *
*  Retour      : Désignation brute du greffon.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *_g_plugin_module_get_modname(const GPluginModule *plugin)
{
    char *result;                           /* Désignation brute à renvoyer*/
    char *path;                             /* Chemin à traiter            */
    char *filename;                         /* Nom de bibliothèque partagée*/
    size_t length;                          /* Taille du nom               */

    path = strdup(g_plugin_module_get_filename(G_PLUGIN_MODULE(plugin)));

    filename = basename(path);

    if (strncmp(filename, "lib", 3) == 0)
        filename += 3;

    length = strlen(filename);

    if (length >= 3)
    {
        if (strncmp(&filename[length - 3], ".so", 3) == 0)
            filename[length - 3] = '\0';
    }

    result = strdup(filename);

    free(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                                                                             *
*  Description : Indique le fichier contenant le greffon manipulé.            *
*                                                                             *
*  Retour      : Chemin d'accès au greffon.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_plugin_module_get_filename(const GPluginModule *plugin)
{
    return plugin->filename;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                                                                             *
*  Description : Fournit la description du greffon dans son intégralité.      *
*                                                                             *
*  Retour      : Interfaçage renseigné.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const plugin_interface *g_plugin_module_get_interface(const GPluginModule *plugin)
{
    return plugin->interface;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                                                                             *
*  Description : Fournit des indications sur l'état du greffon.               *
*                                                                             *
*  Retour      : Fanions portant des indications.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PluginStatusFlags g_plugin_module_get_flags(const GPluginModule *plugin)
{
    return plugin->flags;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à modifier.                                 *
*                flags  = fanions à ajouter brutalement au greffon.           *
*                                                                             *
*  Description : Ajoute des indications sur l'état du greffon.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_override_flags(GPluginModule *plugin, PluginStatusFlags flags)
{
    plugin->flags |= flags;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à mettre à jour.                            *
*                list   = ensemble des greffons disponibles.                  *
*                count  = taille de cet ensemble.                             *
*                                                                             *
*  Description : Met à jour l'ensemble des dépendances du greffon.            *
*                                                                             *
*  Retour      : true si la liste des dépendances a évolué.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_plugin_module_resolve_dependencies(GPluginModule *plugin, GPluginModule **list, size_t count)
{
    bool result;                            /* Bilan à faire remonter      */
    const plugin_interface *pg_iface;       /* Définition du greffon       */
    bitfield_t *new;                        /* Nouvelle définition         */
    size_t i;                               /* Boucle de parcours          */
    GPluginModule *dependency;              /* Module nécessaire           */
    size_t index;                           /* Indice de greffon visé      */

    result = false;

    if (plugin->dependencies == NULL)
        plugin->dependencies = create_bit_field(count, false);

#ifndef NDEBUG
    else
        assert(count == get_bit_field_size(plugin->dependencies));
#endif

    if ((plugin->flags & (PSF_UNKNOW_DEP | PSF_DEP_LOOP)) == 0)
    {
        pg_iface = g_plugin_module_get_interface(plugin);

        /* Collecte des dépendances */

        new = dup_bit_field(plugin->dependencies);

        for (i = 0; i < pg_iface->required_count; i++)
        {
            dependency = get_plugin_by_name(pg_iface->required[i], &index);

            if (dependency == NULL)
                plugin->flags |= PSF_UNKNOW_DEP;

            else
            {
                if (dependency->dependencies == NULL)
                    dependency->dependencies = create_bit_field(count, false);

                set_in_bit_field(new, index, 1);
                or_bit_field(new, dependency->dependencies);

                /**
                 * Si la référence pour dépendance a déjà été prise.
                 */

                if (test_in_bit_field(plugin->dependencies, index))
                    g_object_unref(G_OBJECT(dependency));

            }

        }

        /* Mise à jour du suivi */

        if (compare_bit_fields(plugin->dependencies, new) != 0)
        {
            copy_bit_field(plugin->dependencies, new);
            result = true;
        }

        delete_bit_field(new);

        /* Vérification sanitaire */

        dependency = get_plugin_by_name(pg_iface->name, &index);
        assert(dependency != NULL);

        if (test_in_bit_field(plugin->dependencies, index))
            plugin->flags |= PSF_DEP_LOOP;

        g_object_unref(G_OBJECT(dependency));


    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à valider.                                  *
*                list   = ensemble des greffons disponibles.                  *
*                count  = taille de cet ensemble.                             *
*                                                                             *
*  Description : Termine le chargement du greffon préparé.                    *
*                                                                             *
*  Retour      : Bilan du chargement effectif.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_plugin_module_load(GPluginModule *plugin, GPluginModule **list, size_t count)
{
    bool result;                            /* Bilan à retourner           */
    PluginStatusFlags flags;                /* Fanions de greffon          */
    const plugin_interface *pg_iface;       /* Définition du greffon       */
    size_t i;                               /* Boucle de parcours          */
    GPluginModule *dependency;              /* Module nécessaire           */
    GPluginModuleClass *class;              /* Classe de l'instance active */
    GGenConfig *config;                     /* Configuration à charger     */
    char *dir;                              /* Répertoire modifiable       */

    /* Si un essai précédent a déjà échoué ou réussi... */

    flags = g_plugin_module_get_flags(plugin);

    if (flags & BROKEN_PLUGIN_STATUS) return false;

    if (flags & PSF_LOADED) return true;

    /* Chargement des dépendances */

    pg_iface = g_plugin_module_get_interface(plugin);

    result = true;

    for (i = 0; i < pg_iface->required_count && result; i++)
    {
        dependency = get_plugin_by_name(pg_iface->required[i], NULL);
        assert(dependency != NULL);

        result = g_plugin_module_load(dependency, list, count);

        g_object_unref(G_OBJECT(dependency));

    }

    if (!result)
    {
        log_variadic_message(LMT_ERROR,
                             _("Some dependencies failed to load for plugin '%s'"), plugin->filename);
        goto failure;
    }

    /* Chargement du greffon courant */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    if (class->init != NULL)
    {
        result = class->init(plugin);

        if (!result)
        {
            log_variadic_message(LMT_ERROR,
                                 _("Plugin '%s' failed to load itself..."), plugin->filename);

            plugin->flags |= PSF_FAILURE;
            goto failure;

        }

    }

    g_plugin_module_create_config(plugin);

    result = g_plugin_module_manage(plugin, PGA_PLUGIN_LOADED);

    if (!result)
    {
        log_variadic_message(LMT_ERROR,
                             _("Plugin '%s' failed to complete loading..."), plugin->filename);

        plugin->flags |= PSF_FAILURE;
        goto failure;

    }

    config = g_plugin_module_get_config(plugin);
    g_generic_config_read(config);
    g_object_unref(G_OBJECT(config));

    dir = strdup(plugin->filename);
    dir = dirname(dir);

    log_variadic_message(LMT_PROCESS,
                         _("Loaded the '<b>%s</b>' file as plugin from the '<b>%s</b>' directory"),
                         strrchr(plugin->filename, G_DIR_SEPARATOR) + 1, dir);

    free(dir);

    plugin->flags |= PSF_LOADED;

 failure:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                final  = fin imposée du nom de fichier final.                *
*                create = amorce la création des répertoire ?                 *
*                                                                             *
*  Description : Construit le nom d'un fichier de configuration du greffon.   *
*                                                                             *
*  Retour      : Chemin d'accès déterminé, ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_plugin_module_build_config_filename(const GPluginModule *plugin, const char *final, bool create)
{
    char *result;                           /* Chaîne à retourner          */
    char *modname;                          /* Désignation brute de greffon*/
    char *suffix;                           /* Fin du répertoire personnel */
    bool status;                            /* Bilan d'une création        */

    modname = g_plugin_module_get_modname(plugin);

    suffix = strdup("chrysalide");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, "plugins");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, modname);
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, final);

    result = get_xdg_config_dir(suffix);

    free(suffix);
    free(modname);

    if (create)
    {
        status = mkpath(result);

        if (!status)
        {
            free(result);
            result = NULL;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à compléter.                                *
*                                                                             *
*  Description : Met en place la configuration dédiée au greffon.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_create_config(GPluginModule *plugin)
{
    char *filename;                         /* Chemin d'accès particulier  */

    filename = g_plugin_module_build_config_filename(plugin, "config.xml", false);

    plugin->config = g_generic_config_new_from_file(filename);

    free(filename);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                                                                             *
*  Description : Fournit la configuration mise en place pour le greffon.      *
*                                                                             *
*  Retour      : Configuration dédiée à l'extension.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGenConfig *g_plugin_module_get_config(const GPluginModule *plugin)
{
    GGenConfig *result;                     /* Configuration à faire suivre*/

    result = plugin->config;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                msg    = message à faire apparaître à l'écran.               *
*                                                                             *
*  Description : Présente dans le journal un message simple.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_log_simple_message(const GPluginModule *plugin, LogMessageType type, const char *msg)
{
    size_t len;                             /* Taille tampon disponible    */
    char *buffer;                           /* Tampon du msg reconstitué   */

    len = 4 + strlen(plugin->interface->name) + 6 + strlen(msg) + 1;
    buffer = calloc(len, sizeof(char));

    strcpy(buffer, "<i>[");
    strcat(buffer, plugin->interface->name);
    strcat(buffer, "]</i> ");
    strcat(buffer, msg);

    log_simple_message(type, buffer);

    free(buffer);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                type   = espèce du message à ajouter.                        *
*                fmt    = format du message à faire apparaître à l'écran.     *
*                ...    = éventuels arguments venant compléter le message.    *
*                                                                             *
*  Description : Présente dans le journal un message complexe.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_log_variadic_message(const GPluginModule *plugin, LogMessageType type, const char *fmt, ...)
{
    va_list ap;                             /* Liste d'arguments variable  */
    char *buffer;                           /* Tampon du msg reconstitué   */

    va_start(ap, fmt);
    buffer = build_variadic_message(fmt, ap);
    va_end(ap);

    if (buffer != NULL)
    {
        g_plugin_module_log_simple_message(plugin, type, buffer);

        free(buffer);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                                                                             *
*  Description : Encadre une étape de la vie d'un greffon.                    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_plugin_module_manage(GPluginModule *plugin, PluginAction action)
{
    bool result;                            /* Bilan à faire remonter      */
    GPluginModuleClass *class;              /* Classe de l'instance active */
    const plugin_interface *pg_iface;       /* Informations à consulter    */
    size_t i;                               /* Boucle de parcours          */
    bool handle_action;                     /* Action supportée ?          */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    if (class->manage == NULL)
        result = true;

    else
    {
        handle_action = false;

        pg_iface = g_plugin_module_get_interface(plugin);

        for (i = 0; i < pg_iface->actions_count; i++)
            if (pg_iface->actions[i] == PGA_PLUGIN_LOADED)
            {
                handle_action = true;
                break;
            }

        if (handle_action)
            result = class->manage(plugin/*, action*/);
        else
            result = true;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                unused = variable non utilisé pour l'usage de __VA_ARGS__.   *
*                                                                             *
*  Description : Accompagne la fin du chargement des modules.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_notify_plugins_loaded(GPluginModule *plugin, PluginAction action, void *unused)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->plugins_loaded(plugin, action);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                type   = type d'objet à mettre en place.                     *
*                                                                             *
*  Description : Crée une instance à partir d'un type dynamique externe.      *
*                                                                             *
*  Retour      : Instance d'objet gérée par l'extension ou NULL.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gpointer g_plugin_module_build_type_instance(GPluginModule *plugin, PluginAction action, GType type)
{
    gpointer result;                        /* Instance à retourner        */
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    result = class->build_instance(plugin, action, type);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin    = greffon à manipuler.                             *
*                action    = type d'action attendue.                          *
*                dark      = indique une préférence pour la variante foncée.  *
*                resources = liste de ressources à constituer. [OUT]          *
*                count     = taille de cette liste. [OUT]                     *
*                                                                             *
*  Description : Complète une liste de resources pour thème.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_include_theme(const GPluginModule *plugin, PluginAction action, gboolean dark, char ***resources, size_t *count)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->include_theme(plugin, action, dark, resources, count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                item   = nouveau panneau créé.                               *
*                                                                             *
*  Description : Rend compte de la création d'un panneau.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_notify_panel_creation(const GPluginModule *plugin, PluginAction action, GPanelItem *item)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->notify_panel(plugin, action, item);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                item   = panneau marqué par un changement d'affichage.       *
*                dock   = indique une accroche et non un décrochage.          *
*                                                                             *
*  Description : Rend compte d'un affichage ou d'un retrait de panneau.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_notify_panel_docking(const GPluginModule *plugin, PluginAction action, GPanelItem *item, bool dock)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->notify_docking(plugin, action, item, dock);

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = contenu binaire à traiter.                         *
*                wid     = identifiant du groupe de traitement.               *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Procède à une opération liée à un contenu binaire.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_handle_binary_content(const GPluginModule *plugin, PluginAction action, GBinContent *content, wgroup_id_t wid, GtkStatusStack *status)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->handle_content(plugin, action, content, wid, status);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = contenu chargé à traiter.                          *
*                gid     = identifiant du groupe de traitement.               *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Procède à une opération liée à un contenu chargé.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_handle_loaded_content(const GPluginModule *plugin, PluginAction action, GLoadedContent *content, wgroup_id_t gid, GtkStatusStack *status)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    return class->handle_loaded(plugin, action, content, gid, status);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Procède à une opération liée à l'analyse d'un format.        *
*                                                                             *
*  Retour      : Bilan de l'exécution du traitement.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_plugin_module_handle_known_format_analysis(const GPluginModule *plugin, PluginAction action, GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    result = class->handle_fmt_analysis(plugin, action, format, gid, status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Procède à un préchargement de format de fichier.             *
*                                                                             *
*  Retour      : Bilan de l'exécution du traitement.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_plugin_module_preload_binary_format(const GPluginModule *plugin, PluginAction action, GBinFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    return class->preload_format(plugin, action, format, info, status);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                                                                             *
*  Description : Procède au rattachement d'éventuelles infos de débogage.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_attach_debug_format(const GPluginModule *plugin, PluginAction action, GExeFormat *format)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->attach_debug(plugin, action, format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                binary = binaire dont le contenu est en cours de traitement. *
*                status  = barre de statut à tenir informée.                  *
*                context = contexte de désassemblage.                         *
*                                                                             *
*  Description : Exécute une action pendant un désassemblage de binaire.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_process_disassembly_event(const GPluginModule *plugin, PluginAction action, GLoadedBinary *binary, GtkStatusStack *status, GProcContext *context)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->process_disass(plugin, action, binary, status, context);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = élément chargé à consulter.                        *
*                version = précise si les versions doivent être recherchées.  *
*                names   = désignations humaines correspondantes, à libérer.  *
*                count   = nombre de types d'obscurcissement trouvés. [OUT]   *
*                                                                             *
*  Description : Effectue la détection d'effets d'outils externes.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_plugin_module_detect_external_tools(const GPluginModule *plugin, PluginAction action, const GLoadedContent *content, bool version, char ***names, size_t *count)
{
    GPluginModuleClass *class;              /* Classe de l'instance active */

    class = G_PLUGIN_MODULE_GET_CLASS(plugin);

    class->detect(plugin, action, content, version, names, count);

}
