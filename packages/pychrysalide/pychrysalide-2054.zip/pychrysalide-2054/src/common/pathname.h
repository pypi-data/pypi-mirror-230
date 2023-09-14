
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pathname.h - prototypes pour la manipulation de chemins de fichiers
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


#ifndef _COMMON_PATHNAME_H
#define _COMMON_PATHNAME_H


#include <stdbool.h>



/* Calcule le chemin relatif entre deux fichiers donnés. */
char *build_relative_filename(const char *, const char *);

/* Calcule le chemin absolu d'un fichier par rapport à un autre. */
char *build_absolute_filename(const char *, const char *);

/* S'assure que le chemin fourni est bien en place. */
bool mkpath(const char *);



#endif  /* _COMMON_PATHNAME_H */
