
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pproc.h - prototypes pour les remplacements à la volée de chaînes de caractères
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


#ifndef _TOOLS_D2C_PPROC_H
#define _TOOLS_D2C_PPROC_H


#include <stdbool.h>
#include <sys/types.h>



/* Conversion des chaînes en chaînes */
typedef struct _string_exch
{
    const char *src;                        /* Chaîne à trouver            */
    const char *dest;                       /* Chaîne de remplacement      */

} string_exch;

/* Pré-processeur avec support des macros */
typedef struct _pre_processor pre_processor;


/* Crée un nouveau pre-processeur pour le support des macros. */
pre_processor *create_pre_processor(void);

/* Supprime de la mémoire un pré-processeur et ses macros. */
void delete_pre_processor(pre_processor *);

/* Enregistre une correspondance nule en matière d'encodage. */
void register_empty_encoding(pre_processor *);

/* Enregistre une correspondance en matière d'encodage. */
void register_encoding(pre_processor *, const char *, const char *);

/* Indique le nombre de catégories d'encodages enregistrées. */
size_t count_encodings(const pre_processor *);

/* Fournit une catégorie d'encodage donnée. */
const string_exch *find_encoding(const pre_processor *, size_t);

/* Constitue la matière d'un système de macros. */
void define_macro(pre_processor *, const char *, const char *);

/* Recherche l'existence d'une macro pour un remplacement. */
const char *find_macro(const pre_processor *, const char *);

/* Mémorise une fonction comme produisant un opérateur final. */
void register_as_operand_producer(pre_processor *, const char *);

/* Détermine si une fonction produit un opérande ou non. */
bool is_operand_producer(const pre_processor *, const char *);



#endif  /* _TOOLS_D2C_PPROC_H */
