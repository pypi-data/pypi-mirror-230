
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour la compréhension et la manipulation des champs de bits
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _TOOLS_D2C_BITS_MANAGER_H
#define _TOOLS_D2C_BITS_MANAGER_H


#include <stdbool.h>




/* --------------------------- GESTION DES CHAMPS DE BITS --------------------------- */


/* Elément d'un mot décodé */
typedef struct _raw_bitfield raw_bitfield;



/* Indique le nombre de bits utilisés par le champ. */
unsigned int get_raw_bitfield_length(const raw_bitfield *);

/* Marque un champ de bits comme étant utile. */
void mark_raw_bitfield_as_used(raw_bitfield *);

/* Imprime la désignation d'un champ de bits dans du code. */
void write_raw_bitfield(const raw_bitfield *, int);




/* Représentation de l'ensemble des bits de codage */
typedef struct _coding_bits coding_bits;



/* Crée un nouveau gestionnaire des bits d'encodage brut. */
coding_bits *create_coding_bits(void);

/* Supprime de la mémoire un gestionnaire de bits d'encodage. */
void delete_coding_bits(coding_bits *);



/* Note la présence d'un champ remarquable dans une définition. */
void register_named_field_in_bits(coding_bits *, char *, unsigned int);

/* Note la présence d'un bit invariable dans une définition. */
void register_bit_in_bits(coding_bits *, int);

/* Indique le nombre de bits traités. */
unsigned int count_coded_bits(const coding_bits *);

/* Recherche un champ donné dans un ensemble de champs de bits. */
raw_bitfield *find_named_field_in_bits(const coding_bits *, const char *);

/* Déclare les variables C associées aux champs de bits. */
bool declare_used_bits_fields(const coding_bits *, int);

/* Vérifie que les bits fixes correspondent au masque attendu. */
bool check_bits_correctness(const coding_bits *, int);

/* Définit les variables C associées aux champs de bits. */
bool define_used_bits_fields(const coding_bits *, int);



#endif  /* _TOOLS_D2C_BITS_MANAGER_H */
