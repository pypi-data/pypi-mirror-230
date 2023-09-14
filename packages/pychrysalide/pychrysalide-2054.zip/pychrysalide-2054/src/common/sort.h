
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sort.h - prototypes pour les opérations sur des tableaux triés
 *
 * Copyright (C) 2016-2020 Cyrille Bagard
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


#ifndef _COMMON_SORT_H
#define _COMMON_SORT_H


#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>



/* Compare un booléen avec une autre. */
int sort_boolean(bool, bool);

/* Compare une valeur avec une autre. */
int sort_unsigned_long(unsigned long, unsigned long);

/* Compare une valeur avec une autre. */
int sort_signed_long_long(signed long long, signed long long);

/* Compare une valeur avec une autre. */
int sort_unsigned_long_long(unsigned long long, unsigned long long);

/* Compare une valeur de 64 bits avec une autre. */
int sort_uint64_t(uint64_t, uint64_t);

/* Compare un pointeur avec un autre. */
int sort_pointer(const void *, const void *, __compar_fn_t);

/* Effectue une recherche dichotomique dans un tableau. */
bool bsearch_index(const void *, const void *, size_t, size_t, __compar_fn_t, size_t *);

/* Ajoute à l'endroit indiqué un élément dans un tableau. */
void *_qinsert(void *, size_t *, size_t, void *, size_t);

/* Ajoute à l'endroit indiqué des éléments dans un tableau. */
void *_qinsert_batch(void *, size_t *, size_t, void *, size_t, size_t);

/* Ajoute au bon endroit un élément dans un tableau trié. */
void *qinsert(void *, size_t *, size_t, __compar_fn_t, void *);

/* Ajoute au bon endroit un élément dans un tableau trié. */
void *qinsert_multi(void *, size_t *, size_t, __compar_fn_t, void *);

/* Supprime un élément dans un tableau trié. */
void *_qdelete(void *, size_t *, size_t, size_t);

/* Supprime un élément dans un tableau trié. */
void *qdelete(void *, size_t *, size_t, __compar_fn_t, void *);



#endif  /* _COMMON_SORT_H */
