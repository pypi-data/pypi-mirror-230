
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cpp.h - prototypes pour avoir à disposition un langage C plus plus mieux
 *
 * Copyright (C) 2010-2020 Cyrille Bagard
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


#ifndef _COMMON_CPP_H
#define _COMMON_CPP_H


#include <limits.h>
#include <string.h>



/**
 * Fournit la taille d'un tableau statique.
 */
#define ARRAY_SIZE(a) (sizeof(a) / sizeof(a[0]))


/**
 * Détermine la taille de la plus longue chaîne de caractères
 * correspondant à un type donné.
 */

#define XSTR(e) STR(e)
#define STR(e) #e

#define SIZE_T_MAXLEN strlen(XSTR(LONG_MAX))

#define ULLONG_MAXLEN (sizeof(XSTR(ULLONG_MAX)) + 1)


/**
 * Emprunt au noyau Linux (cf. include/linux/bug.h) pour les vérifications à la compilation.
 */

#define BUILD_BUG_ON(cond) (((void)sizeof(char[1 - 2 * !!(cond)])))



#endif  /* _COMMON_CPP_H */
