
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bits.h - prototypes pour la manipulation d'un champ de bits quelconque
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


#ifndef _COMMON_BITS_H
#define _COMMON_BITS_H


#include "../arch/vmpa.h"



/* Champ de bits simple */
typedef struct _bitfield_t bitfield_t;


/* Crée un champ de bits initialisé. */
bitfield_t *create_bit_field(size_t, bool);

/* Crée une copie d'un champ de bits classique. */
bitfield_t *dup_bit_field(const bitfield_t *);

/* Supprime de la mémoire un champ de bits donné. */
void delete_bit_field(bitfield_t *);

/* Copie un champ de bits dans un autre. */
void copy_bit_field(bitfield_t *, const bitfield_t *);

/* Redimensionne un champ de bits. */
void resize_bit_field(bitfield_t **, size_t);

/* Indique la taille d'un champ de bits donné. */
size_t get_bit_field_size(const bitfield_t *);

/* Compare deux champs de bits entre eux. */
int compare_bit_fields(const bitfield_t *, const bitfield_t *);

/* Bascule à 0 un champ de bits dans son intégralité. */
void reset_all_in_bit_field(bitfield_t *);

/* Bascule à 1 un champ de bits dans son intégralité. */
void set_all_in_bit_field(bitfield_t *);

/* Bascule à 0 une partie d'un champ de bits. */
void reset_in_bit_field(bitfield_t *, size_t, size_t);

/* Bascule à 1 une partie d'un champ de bits. */
void set_in_bit_field(bitfield_t *, size_t, size_t);

/* Réalise une opération ET logique entre deux champs de bits. */
void and_bit_field(bitfield_t *, const bitfield_t *);

/* Réalise une opération OU logique entre deux champs de bits. */
void or_bit_field(bitfield_t *, const bitfield_t *);

/* Réalise une opération OU logique entre deux champs de bits. */
void or_bit_field_at(bitfield_t *, const bitfield_t *, size_t);

/* Détermine si un bit est à 1 dans un champ de bits. */
bool test_in_bit_field(const bitfield_t *, size_t);

/* Détermine si un ensemble de bits est à 0 dans un champ. */
bool test_none_in_bit_field(const bitfield_t *, size_t, size_t);

/* Détermine si un ensemble de bits est à 1 dans un champ. */
bool test_all_in_bit_field(const bitfield_t *, size_t, size_t);

/* Teste l'état à 0 de bits selon un masque de bits. */
bool test_zeros_within_bit_field(const bitfield_t *, size_t, const bitfield_t *);

/* Teste l'état à 1 de bits selon un masque de bits. */
bool test_ones_within_bit_field(const bitfield_t *, size_t, const bitfield_t *);

/* Détermine le nombre de bits à 1 dans un champ. */
size_t popcount_for_bit_field(const bitfield_t *);



#endif  /* _COMMON_BITS_H */
