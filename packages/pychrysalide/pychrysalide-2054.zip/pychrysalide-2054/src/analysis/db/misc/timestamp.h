
/* Chrysalide - Outil d'analyse de fichiers binaires
 * timestamp.h - prototypes pour l'encodage par plage unique d'une chaîne de caractères
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_MISC_TIMESTAMP_H
#define _ANALYSIS_DB_MISC_TIMESTAMP_H


#include <stdbool.h>
#include <stdint.h>


#include "../../../common/packed.h"
#include "../../../common/sqlite.h"



/* Représentation d'un horodatage */
typedef uint64_t timestamp_t;


/* Prépare un horodatage à une définition. */
void setup_empty_timestamp(timestamp_t *);

/* Obtient un horodatage initialisé au moment même. */
bool init_timestamp(timestamp_t *);

/* Obtient un horodatage initialisé avec une valeur donnée. */
bool init_timestamp_from_value(timestamp_t *, uint64_t);

/* Définit si un horodatage est plus récent qu'un autre ou non. */
bool timestamp_is_younger(timestamp_t, timestamp_t);

/* Effectue une copie d'horodatage. */
void copy_timestamp(timestamp_t *, const timestamp_t *);

/* Effectue la comparaison entre deux horodatages. */
int cmp_timestamp(const timestamp_t *, const timestamp_t *);

/* Importe la définition d'un horodatage. */
bool unpack_timestamp(timestamp_t *, packed_buffer_t *);

/* Exporte la définition d'un horodatage. */
bool pack_timestamp(const timestamp_t *, packed_buffer_t *);



/* --------------------- MANIPULATIONS AVEC UNE BASE DE DONNEES --------------------- */


/* Définition du tronc commun pour les créations SQLite */
#define SQLITE_TIMESTAMP_CREATE(n)      \
    n " INTEGER"

/* Charge les valeurs utiles pour un horodatage. */
bool load_timestamp(timestamp_t *, const char *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
bool store_timestamp(const timestamp_t *, const char *, bound_value **, size_t *);



#endif  /* _ANALYSIS_DB_MISC_TIMESTAMP_H */
