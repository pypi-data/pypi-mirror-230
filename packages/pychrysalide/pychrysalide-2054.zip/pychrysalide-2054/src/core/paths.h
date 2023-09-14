
/* Chrysalide - Outil d'analyse de fichiers binaires
 * paths.h - prototypes pour la récupération de fichiers secondaires
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _CORE_PATHS_H
#define _CORE_PATHS_H



/* Enregistre un répertoire comme nouvelle base de construction. */
void register_new_prefix(const char *);

/* Fournit le répertoire réel correspondant à une cible. */
char *get_effective_directory(const char *);

/* Listes de répertoires d'installation */
typedef enum _TargetDirectoryType
{
    TDT_PLUGINS_LIB,                        /* Répertoire des extensions   */

} TargetDirectoryType;

/* Fournit le répertoire réel correspondant à une cible. */
char *get_effective_directory_new(TargetDirectoryType);

/* Trouve le chemin d'accès complet à un fichier d'image. */
char *find_pixmap_file(const char *);

/* Trouve le chemin d'accès complet à un fichier de greffon. */
char *find_plugin_data_file(const char *, const char *);



#endif  /* _CORE_PATHS_H */
