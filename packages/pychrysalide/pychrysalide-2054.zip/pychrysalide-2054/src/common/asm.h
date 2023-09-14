
/* Chrysalide - Outil d'analyse de fichiers binaires
 * asm.h - prototypes pour les implémentations génériques de fonctionnalités spécifiques
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _COMMON_ASM_H
#define _COMMON_ASM_H


#include <stdbool.h>
#include <stdint.h>



/* Détermine l'indice du premier bit à 1, côté gauche. */
bool msb_32(uint32_t, unsigned int *);

/* Détermine l'indice du premier bit à 1, côté gauche. */
bool msb_64(uint64_t, unsigned int *);

/* Détermine le nombre de bits à 1 dans une valeur de 32 bits. */
unsigned int popcount_32(uint32_t v);

/* Détermine le nombre de bits à 1 dans une valeur de 64 bits. */
unsigned int popcount_64(uint64_t v);



#endif  /* _COMMON_ASM_H */
