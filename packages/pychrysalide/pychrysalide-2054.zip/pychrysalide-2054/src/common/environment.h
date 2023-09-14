
/* Chrysalide - Outil d'analyse de fichiers binaires
 * environment.h - prototypes pour la manipulations des variables d'environnement.
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _COMMON_ENVIRONMENT_H
#define _COMMON_ENVIRONMENT_H


#include <stdbool.h>



/* Fournit le contenu d'une variable d'environnement. */
char *get_env_var(const char *);

/* Complète le contenu d'une variable d'environnement. */
bool add_to_env_var(const char *, const char *, const char *);



#endif  /* _COMMON_ENVIRONMENT_H */
