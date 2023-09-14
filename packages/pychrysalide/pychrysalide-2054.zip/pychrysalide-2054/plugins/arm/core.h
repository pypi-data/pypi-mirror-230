
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.h - prototypes pour l'intégration du support de l'architecture ARM
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ARM_CORE_H
#define _PLUGINS_ARM_CORE_H


#include <plugins/plugin.h>
#include <plugins/plugin-int.h>



/* Prend acte du chargement du greffon. */
G_MODULE_EXPORT bool chrysalide_plugin_init(GPluginModule *);

/* Prend acte du déchargement du greffon. */
G_MODULE_EXPORT void chrysalide_plugin_exit(GPluginModule *);



#endif  /* _PLUGINS_ARM_CORE_H */
