
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fnv1a.h - prototypes pour l'implémentaton du calcul rapide d'empreintes de chaînes
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


#ifndef _COMMON_FNV1A_H
#define _COMMON_FNV1A_H


#include <stdbool.h>
#include <stdint.h>


/**
 * Plus d'informations avec les liens suivants :
 *  - http://en.wikipedia.org/wiki/Fowler-Noll-Vo_hash_function
 *  - http://isthe.com/chongo/tech/comp/fnv/
 */


/* Détermination d'un type à part */
typedef uint64_t fnv64_t;


/* Détermine si deux empreintes FNV1a sont indentiques ou non. */
int cmp_fnv_64a(fnv64_t, fnv64_t);

/* Détermine l'empreinte FNV1a d'une chaîne de caractères. */
fnv64_t fnv_64a_hash(const char *);



#endif  /* _COMMON_FNV1A_H */
