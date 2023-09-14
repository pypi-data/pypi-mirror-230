
/* Chrysalide - Outil d'analyse de fichiers binaires
 * self.h - définitions pour inclusion dans les différents greffons
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _PLUGINS_SELF_H
#define _PLUGINS_SELF_H


#ifndef _PLUGINS_PLUGIN_H
#   include "plugin.h"
#endif



/* Facilitations de déclarations */

#define CHRYSALIDE_WEBSITE(p) "https://www.chrysalide.re/" p

#define EMPTY_PG_LIST(name)                         \
    name = NULL,                                    \
    name ## _count = 0                              \

#define BUILD_PG_LIST(name, lst)                    \
    name = lst,                                     \
    name ## _count = sizeof(lst) / sizeof(lst[0])   \

#define AL(...) BUILD_PG_LIST(.actions, ((plugin_action_t []){ __VA_ARGS__ }))

#define RL(...) BUILD_PG_LIST(.required, ((char *[]){ __VA_ARGS__ }))

#define NO_REQ EMPTY_PG_LIST(.required)


/* Composants d'interface */

#define __private __attribute__((visibility("hidden")))

#define PLUGIN_CORE_SELF                                                                    \
static GPluginModule *_this_plugin = NULL;                                                  \
G_MODULE_EXPORT void chrysalide_plugin_set_self(GPluginModule *p);                          \
G_MODULE_EXPORT void chrysalide_plugin_set_self(GPluginModule *p) { _this_plugin = p; };    \
__private GPluginModule *_chrysalide_plugin_get_self(void);                                 \
__private GPluginModule *_chrysalide_plugin_get_self(void) { return _this_plugin; };

#define PLUGIN_CORE_PROPS(n, d, v, u, c)                        \
                                                                \
    .magic = CHRYSALIDE_PLUGIN_MAGIC,                           \
    .abi_version = CURRENT_ABI_VERSION,                         \
                                                                \
    .gtp_name = "G" n "Plugin",                                 \
    .name = n,                                                  \
    .desc = d,                                                  \
    .version = v,                                               \
    .url = u,                                                   \
                                                                \
    .container = c

#define DEFINE_CHRYSALIDE_PLUGIN(n, d, v, u, r, a)              \
PLUGIN_CORE_SELF                                                \
G_MODULE_EXPORT const plugin_interface _chrysalide_plugin = {   \
    PLUGIN_CORE_PROPS(n, d, v, u, false),                       \
    r,                                                          \
    a,                                                          \
}

#define DEFINE_CHRYSALIDE_CONTAINER_PLUGIN(n, d, v, u, r, a)    \
PLUGIN_CORE_SELF                                                \
G_MODULE_EXPORT const plugin_interface _chrysalide_plugin = {   \
    PLUGIN_CORE_PROPS(n, d, v, u, true),                        \
    r,                                                          \
    a,                                                          \
}


/* Manipulations accélérées */

__private GPluginModule *_chrysalide_plugin_get_self(void);

#define log_plugin_simple_message(type, msg)                                        \
    do                                                                              \
    {                                                                               \
        GPluginModule *__this;                                                      \
        __this = _chrysalide_plugin_get_self();                                     \
        if (__this != NULL)                                                         \
            g_plugin_module_log_simple_message(__this, type, msg);                  \
        else                                                                        \
            log_simple_message(type, msg);                                          \
    }                                                                               \
    while (0)

#define log_plugin_variadic_message(type, msg, ...)                                 \
    do                                                                              \
    {                                                                               \
        GPluginModule *__this;                                                      \
        __this = _chrysalide_plugin_get_self();                                     \
        if (__this != NULL)                                                         \
            g_plugin_module_log_variadic_message(__this, type, msg, __VA_ARGS__);   \
        else                                                                        \
            log_variadic_message(type, msg, __VA_ARGS__);                           \
    }                                                                               \
    while (0)



#endif  /* _PLUGINS_SELF_H */
