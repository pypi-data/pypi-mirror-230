
/* Chrysalide - Outil d'analyse de fichiers binaires
 * snapshot.h - prototypes pour la gestion des instantanés de bases de données
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


#ifndef _ANALYSIS_DB_SNAPSHOT_H
#define _ANALYSIS_DB_SNAPSHOT_H


#include <archive.h>
#include <glib-object.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>


#include "cdb.h"
#include "protocol.h"
#include "misc/snapshot.h"



#define G_TYPE_DB_SNAPSHOT            g_db_snapshot_get_type()
#define G_DB_SNAPSHOT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DB_SNAPSHOT, GDbSnapshot))
#define G_IS_DB_SNAPSHOT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DB_SNAPSHOT))
#define G_DB_SNAPSHOT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_SNAPSHOT, GDbSnapshotClass))
#define G_IS_DB_SNAPSHOT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_SNAPSHOT))
#define G_DB_SNAPSHOT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_SNAPSHOT, GDbSnapshotClass))


/* Gestionnaire d'instantanés de bases de données (instance) */
typedef struct _GDbSnapshot GDbSnapshot;

/* Gestionnaire d'instantanés de bases de données (classe) */
typedef struct _GDbSnapshotClass GDbSnapshotClass;


/* Indique le type défini pour un gestionnaire d'instantanés de bases de données. */
GType g_db_snapshot_get_type(void);

/* Prépare un gestionnaire d'instantanés de bases de données. */
GDbSnapshot *g_db_snapshot_new_empty(const GCdbArchive *, GList *);

/* Charge un gestionnaire d'instantanés de bases de données. */
GDbSnapshot *g_db_snapshot_new_from_xml(const GCdbArchive *, xmlDocPtr, xmlXPathContextPtr);

/* Associe une base de données aux instantanés chargés. */
bool g_db_snapshot_fill(GDbSnapshot *, struct archive *, const GCdbArchive *);

/* Enregistre tous les éléments associés aux instantanés. */
DBError g_db_snapshot_save(const GDbSnapshot *, xmlDocPtr, xmlXPathContextPtr, struct archive *);

/* Fournit l'identifiant de l'instanné courant. */
bool g_db_snapshot_get_current_id(const GDbSnapshot *, snapshot_id_t *);

/* Fournit la base de données correspondant à instanné donné. */
sqlite3 *g_db_snapshot_get_database(const GDbSnapshot *);

/* Collecte les descriptions de l'ensemble des instantanés. */
bool g_db_snapshot_pack_all(const GDbSnapshot *, packed_buffer_t *);

/* Actualise la désignation d'un instantané donné. */
DBError g_db_snapshot_set_name(const GDbSnapshot *, packed_buffer_t *);

/* Actualise la description d'un instantané donné. */
DBError g_db_snapshot_set_desc(const GDbSnapshot *, packed_buffer_t *);

/* Restaure un instantané de l'arborescence. */
DBError g_db_snapshot_restore(GDbSnapshot *, packed_buffer_t *, bool *);

/* Crée un nouvel instantanés dans l'arborescence. */
DBError g_db_snapshot_create(GDbSnapshot *, sqlite3 *, const GCdbArchive *);

/* Supprime un instantané dans l'arborescence. */
DBError g_db_snapshot_remove(GDbSnapshot *, packed_buffer_t *, bool *);



#endif  /* _ANALYSIS_DB_SNAPSHOT_H */
