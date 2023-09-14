
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pearson.h - prototypes pour l'implémentaton du calcul rapide d'empreintes de chaînes
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _COMMON_PEARSON_H
#define _COMMON_PEARSON_H


#include <stdint.h>


/**
 * Plus d'informations avec les liens suivants :
 *  - https://en.wikipedia.org/wiki/Pearson_hashing
 *  - https://web.archive.org/web/20120704025921/http://cs.mwsu.edu/~griffin/courses/2133/downloads/Spring11/p677-pearson.pdf
 */


/* Fournit les permutations par défaut par Pearson. */
const char *get_pearson_permutations(void);

/* Détermine l'empreinte Pearson d'une chaîne de caractères. */
uint8_t pearson_hash(const char *, const char *);



#endif  /* _COMMON_PEARSON_H */
