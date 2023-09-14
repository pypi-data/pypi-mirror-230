
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pglist.h - prototypes pour la gestion de l'ensemble des greffons
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


#ifndef _PLUGINS_PGLIST_H
#define _PLUGINS_PGLIST_H


#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include "plugin-def.h"
#include "plugin.h"



/* Procède au chargement des différents greffons trouvés. */
bool init_all_plugins(bool);

/* Procède au déchargement des différents greffons présents. */
void exit_all_plugins(void);

/* Verrouille ou déverrouille l'accès en lecture à la liste. */
void _lock_unlock_plugin_list_for_reading(bool lock);

#define lock_plugin_list_for_reading() _lock_unlock_plugin_list_for_reading(true)
#define unlock_plugin_list_for_reading() _lock_unlock_plugin_list_for_reading(false)

/* Ajoute un greffon à la liste principale de greffons. */
void _register_plugin(GPluginModule *);

/* Ajoute un greffon à la liste principale de greffons. */
void register_plugin(GPluginModule *);

/* Charge tous les greffons restant à charger. */
void load_remaning_plugins(void);

/* Fournit le greffon répondant à un nom donné. */
GPluginModule *get_plugin_by_name(const char *, size_t *);

/* Fournit la liste de l'ensemble des greffons. */
GPluginModule **get_all_plugins(size_t *);

/* Fournit les greffons offrant le service demandé. */
GPluginModule **get_all_plugins_for_action(PluginAction, size_t *);



/**
 * Définitions des opérations appliquables à une catégories de greffons.
 */

#define process_all_plugins_for(a, f, ...)                  \
    do                                                      \
    {                                                       \
        size_t __count;                                     \
        GPluginModule **__list;                             \
        size_t __i;                                         \
        __list = get_all_plugins_for_action(a, &__count);   \
        for (__i = 0; __i < __count; __i++)                 \
        {                                                   \
            f(__list[__i], a, __VA_ARGS__);                 \
            g_object_unref(G_OBJECT(__list[__i]));          \
        }                                                   \
        if (__list != NULL)                                 \
            free(__list);                                   \
    }                                                       \
    while (0)

#define process_plugins_while_null(a, f, ...)               \
    ({                                                      \
        void *__result;                                     \
        size_t __count;                                     \
        GPluginModule **__list;                             \
        size_t __i;                                         \
        __result = NULL;                                    \
        __list = get_all_plugins_for_action(a, &__count);   \
        for (__i = 0; __i < __count; __i++)                 \
        {                                                   \
            if (__result == NULL)                           \
                __result = f(__list[__i], a, __VA_ARGS__);  \
            g_object_unref(G_OBJECT(__list[__i]));          \
        }                                                   \
        if (__list != NULL)                                 \
            free(__list);                                   \
        __result;                                           \
    })


/* DPS_PG_MANAGEMENT */

#define notify_native_plugins_loaded() \
    process_all_plugins_for(PGA_NATIVE_PLUGINS_LOADED, g_plugin_module_notify_plugins_loaded, NULL)

#define notify_all_plugins_loaded() \
    process_all_plugins_for(PGA_ALL_PLUGINS_LOADED, g_plugin_module_notify_plugins_loaded, NULL)

#define build_type_instance(t) \
    process_plugins_while_null(PGA_TYPE_BUILDING, g_plugin_module_build_type_instance, t)

/* DPS_SETUP */

#define include_plugin_theme(d, r, c) \
    process_all_plugins_for(PGA_GUI_THEME, g_plugin_module_include_theme, d, r, c)

/* DPS_RUNNING */

#define notify_panel_creation(i) \
    process_all_plugins_for(PGA_PANEL_CREATION, g_plugin_module_notify_panel_creation, i)

#define notify_panel_docking(i, d) \
    process_all_plugins_for(PGA_PANEL_DOCKING, g_plugin_module_notify_panel_docking, i, d)

/* DPS_CONTENT */

#define handle_binary_content(a, c, i, s) \
    process_all_plugins_for(a, g_plugin_module_handle_binary_content, c, i, s)

#define handle_loaded_content(a, c, i, s) \
    process_all_plugins_for(a, g_plugin_module_handle_loaded_content, c, i, s)

/* DPS_FORMAT */

#define handle_known_format_analysis(a, f, g, s) \
    process_all_plugins_for(a, g_plugin_module_handle_known_format_analysis, f, g, s)

#define preload_binary_format(a, f, i, s) \
    process_all_plugins_for(a, g_plugin_module_preload_binary_format, f, i, s)

#define attach_debug_format(f) \
    process_all_plugins_for(PGA_FORMAT_ATTACH_DEBUG, g_plugin_module_attach_debug_format, f)

/* DPS_DISASSEMBLY */

#define process_disassembly_event(a, b, s, c) \
    process_all_plugins_for(a, g_plugin_module_process_disassembly_event, b, s, c)

/* DPS_DETECTION */

#define detect_external_tools(a, cnt, v, n, c) \
    process_all_plugins_for(a, g_plugin_module_detect_external_tools, cnt, v, n, c)



#endif  /* _PLUGINS_PGLIST_H */
