
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rlestr.h - prototypes pour l'encodage par plage unique d'une chaîne de caractères
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_MISC_RLESTR_H
#define _ANALYSIS_DB_MISC_RLESTR_H


#include <stdbool.h>
#include <stdint.h>
#include <sys/types.h>


#include "../../../common/packed.h"
#include "../../../common/sqlite.h"



/* Informations de base pour tout élément ajouté */
typedef struct _rle_string
{
    union
    {
        char *data;                         /* Chaîne de caractères        */
        const char *cst_data;               /* Autre version de chaîne     */
    };

    uint16_t length;                        /* Taille de la chaîne         */
    bool dynamic;                           /* Type d'allocation utilisée  */

} rle_string;


#define setup_empty_rle_string(s) \
    init_static_rle_string(s, NULL);

/* Définit une représentation de chaîne de caractères. */
void init_dynamic_rle_string(rle_string *, char *);

/* Définit une représentation de chaîne de caractères constante. */
void init_static_rle_string(rle_string *, const char *);

/* Copie une chaîne de caractères existante. */
void dup_into_rle_string(rle_string *, const char *);

#define exit_rle_string(rle) unset_rle_string(rle)

#define get_rle_string(rle) (rle)->data

#define get_rle_length(rle) (rle)->length

#define is_rle_string_empty(rle) ((rle)->data == NULL)

/* Constitue une représentation de chaîne de caractères. */
void set_dynamic_rle_string(rle_string *, char *);

/* Constitue une représentation de chaîne de caractères stable. */
void set_static_rle_string(rle_string *, const char *);

/* Libère la mémoire associée à la représentation. */
void unset_rle_string(rle_string *);

/* Effectue la comparaison entre deux chaînes de caractères. */
int cmp_rle_string(const rle_string *, const rle_string *);

/* Importe la définition d'une chaîne de caractères. */
bool unpack_rle_string(rle_string *, packed_buffer_t *);

/* Exporte la définition d'une chaîne de caractères. */
bool pack_rle_string(const rle_string *, packed_buffer_t *);



/* --------------------- MANIPULATIONS AVEC UNE BASE DE DONNEES --------------------- */


/* Définition du tronc commun pour les créations SQLite */
#define SQLITE_RLESTR_CREATE(n)     \
    n " TEXT"

/* Charge les valeurs utiles pour une chaîne de caractères. */
bool load_rle_string(rle_string *, const char *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
bool store_rle_string(const rle_string *, const char *, bound_value **, size_t *);



#endif  /* _ANALYSIS_DB_MISC_RLESTR_H */
