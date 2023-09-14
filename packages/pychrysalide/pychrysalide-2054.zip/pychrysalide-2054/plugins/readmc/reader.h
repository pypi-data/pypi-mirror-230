
/* Chrysalide - Outil d'analyse de fichiers binaires
 * reader.h - prototypes pour l'interprétation des informations secondaires contenues dans un fichier Mobicore
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


#ifndef _PLUGINS_READMC_READER_H
#define _PLUGINS_READMC_READER_H


#include <plugins/plugin.h>
#include <plugins/plugin-int.h>



/* Etablit des symboles complémentaires dans un format Mobicore. */
G_MODULE_EXPORT bool chrysalide_plugin_preload_binary_format(const GPluginModule *, PluginAction, GBinFormat *, GPreloadInfo *, GtkStatusStack *);



#endif  /* _PLUGINS_READMC_READER_H */
