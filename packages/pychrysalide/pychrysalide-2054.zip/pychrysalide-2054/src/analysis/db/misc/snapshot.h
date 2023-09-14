
/* Chrysalide - Outil d'analyse de fichiers binaires
 * snapshot.h - prototypes pour l'encodage des informations utiles aux instantanés
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_MISC_SNAPSHOT_H
#define _ANALYSIS_DB_MISC_SNAPSHOT_H


#include <stdbool.h>
#include <stdint.h>


#include "rlestr.h"
#include "timestamp.h"
#include "../../../common/packed.h"



/* -------------------------- IDENTIFIANTS DES INSTANTANES -------------------------- */


#define SNAP_ID_RAND_SZ 32
#define SNAP_ID_HEX_SZ (SNAP_ID_RAND_SZ * 2 + 1)

/* Représentation d'un instantané */
typedef struct _snapshot_id_t
{
    char name[SNAP_ID_HEX_SZ];              /* Caractères hexadécimaux     */

} snapshot_id_t;


/* Identifiant d'un parent de racine */
#define NO_SNAPSHOT_ROOT "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"


/* Prépare un identifiant pour instantané à une définition. */
void setup_empty_snapshot_id(snapshot_id_t *);

/* Construit un identifiant pour instantané de base de données. */
bool init_snapshot_id(snapshot_id_t *);

/* Construit un identifiant pour instantané de base de données. */
bool init_snapshot_id_from_text(snapshot_id_t *, const char *);

#define snapshot_id_as_string(id) (id)->name

/* Effectue une copie d'identifiant d'instantané. */
void copy_snapshot_id(snapshot_id_t *, const snapshot_id_t *);

/* Effectue la comparaison entre deux identifiants. */
int cmp_snapshot_id(const snapshot_id_t *, const snapshot_id_t *);

/* Importe la définition d'un identifiant d'instantané. */
bool unpack_snapshot_id(snapshot_id_t *, packed_buffer_t *);

/* Exporte la définition d'un identifiant d'instantané. */
bool pack_snapshot_id(const snapshot_id_t *, packed_buffer_t *);



/* --------------------------- PROPRIETES DES INSTANTANES --------------------------- */


/* Description d'un instantané */
typedef struct _snapshot_info_t
{
    snapshot_id_t parent_id;                /* Identifiant du propriétaire */
    snapshot_id_t id;                       /* Identifiant attribué        */

    timestamp_t created;                    /* Date de création            */

    char *name;                             /* Nom de l'instantané         */
    char *desc;                             /* Description associée        */

} snapshot_info_t;


/* Prépare une description pour instantané à une définition. */
void setup_empty_snapshot_info(snapshot_info_t *);

/* Construit une description pour instantané de base de données. */
bool init_snapshot_info(snapshot_info_t *);

/* Construit une description pour instantané de base de données. */
bool init_snapshot_info_from_text(snapshot_info_t *, const char *, uint64_t, const char *, const char *);

/* Libère la mémoire occupée par une description d'instantané. */
void exit_snapshot_info(snapshot_info_t *);

#define get_snapshot_info_parent_id(nfo) &(nfo)->parent_id
#define get_snapshot_info_id(nfo) &(nfo)->id
#define get_snapshot_info_created(nfo) (nfo)->created
#define get_snapshot_info_name(nfo) (nfo)->name
#define get_snapshot_info_desc(nfo) (nfo)->desc

/* Effectue une copie de description d'instantané. */
void copy_snapshot_info(snapshot_info_t *, const snapshot_info_t *);

/* Importe la description d'un identifiant d'instantané. */
bool unpack_snapshot_info(snapshot_info_t *, packed_buffer_t *);

/* Exporte la description d'un identifiant d'instantané. */
bool pack_snapshot_info(const snapshot_info_t *, packed_buffer_t *);

/* Change la désignation dans les informations d'un instantané. */
void set_snapshot_info_name(snapshot_info_t *, const char *);

/* Change la description dans les informations d'un instantané. */
void set_snapshot_info_desc(snapshot_info_t *, const char *);



#endif  /* _ANALYSIS_DB_MISC_SNAPSHOT_H */
