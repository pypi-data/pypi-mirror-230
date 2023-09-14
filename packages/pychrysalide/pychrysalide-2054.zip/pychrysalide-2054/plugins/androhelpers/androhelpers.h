
/* Chrysalide - Outil d'analyse de fichiers binaires
 * androhelpers.h - prototypes pour le greffon d'appoint pour les traitements Android
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ANDROHELPERS_H
#define _PLUGINS_ANDROHELPERS_H


#include <plugins/plugin.h>



/* Précise le nom associé au greffon. */
char *get_plugin_name(void);

/* Indique les opérations offertes par un greffon donné. */
PluginAction get_plugin_action(const GPluginModule *);

/* Exécute une action définie sur un binaire chargé. */
bool execute_action_on_binary(GPluginModule *, GLoadedBinary *, PluginAction);



#endif  /* _PLUGINS_ANDROHELPERS_H */
