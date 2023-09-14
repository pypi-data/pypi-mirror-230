
/* Chrysalide - Outil d'analyse de fichiers binaires
 * speed.h - prototypes pour la mesure de temps d'exécution internes
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _PLUGINS_DEVDBG_SPEED_H
#define _PLUGINS_DEVDBG_SPEED_H


#include <plugins/plugin.h>
#include <plugins/plugin-int.h>



/* Procède à une opération liée à l'analyse d'un format. */
G_MODULE_EXPORT bool chrysalide_plugin_handle_binary_format_analysis(const GPluginModule *, PluginAction, GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Exécute une action pendant un désassemblage de binaire. */
G_MODULE_EXPORT void chrysalide_plugin_process_disassembly_event(const GPluginModule *, PluginAction , GLoadedBinary *, GtkStatusStack *, GProcContext *);



#endif  /* _PLUGINS_DEVDBG_SPEED_H */
