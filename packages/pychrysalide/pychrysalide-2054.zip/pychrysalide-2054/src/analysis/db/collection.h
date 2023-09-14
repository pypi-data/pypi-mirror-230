
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection.h - prototypes pour la gestion d'éléments ajoutés par collection
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


#ifndef _ANALYSIS_DB_COLLECTION_H
#define _ANALYSIS_DB_COLLECTION_H


#include <glib-object.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdint.h>


#include "item.h"
#include "protocol.h"
#include "../../common/packed.h"



#define G_TYPE_DB_COLLECTION            g_db_collection_get_type()
#define G_DB_COLLECTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DB_COLLECTION, GDbCollection))
#define G_IS_DB_COLLECTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DB_COLLECTION))
#define G_DB_COLLECTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_COLLECTION, GDbCollectionClass))
#define G_IS_DB_COLLECTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_COLLECTION))
#define G_DB_COLLECTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_COLLECTION, GDbCollectionClass))


/* Collection générique d'éléments (instance) */
typedef struct _GDbCollection GDbCollection;

/* Collection générique d'éléments (classe) */
typedef struct _GDbCollectionClass GDbCollectionClass;


/* Indique le type défini pour une collection générique d'éléments. */
GType g_db_collection_get_type(void);

/* Prépare la mise en place d'une nouvelle collection. */
GDbCollection *g_db_collection_new(uint32_t, GType, const char *);

/* Attache à une collection un binaire pour les éléments listés. */
void g_db_collection_link_to_binary(GDbCollection *, GLoadedBinary *);

/* Décrit le type des éléments rassemblées dans une collection. */
uint32_t g_db_collection_get_feature(const GDbCollection *);

/* Décrit le type de collection manipulée. */
const char *g_db_collection_get_name(const GDbCollection *);


/* Réceptionne un élément depuis une requête réseau. */
bool _g_db_collection_unpack(GDbCollection *, packed_buffer_t *, DBAction *, GDbItem **);

/* Réceptionne et traite une requête réseau pour collection. */
bool g_db_collection_unpack(GDbCollection *, packed_buffer_t *, sqlite3 *);

/* Envoie pour traitement une requête réseau pour collection. */
bool g_db_collection_pack(GDbCollection *, packed_buffer_t *, DBAction, const GDbItem *);

/* Envoie pour mise à jour tous les éléments courants. */
bool g_db_collection_pack_all_updates(GDbCollection *, packed_buffer_t *);




/* Met à disposition un encadrement des accès aux éléments. */
void g_db_collection_lock_unlock(GDbCollection *, bool, bool);

#define g_db_collection_wlock(col) g_db_collection_lock_unlock(col, true, true);
#define g_db_collection_wunlock(col) g_db_collection_lock_unlock(col, true, false);

#define g_db_collection_rlock(col) g_db_collection_lock_unlock(col, false, true);
#define g_db_collection_runlock(col) g_db_collection_lock_unlock(col, false, false);

/* Renvoie la liste des éléments rassemblés. */
GDbItem **g_db_collection_get_items(const GDbCollection *, size_t *);

/* Renvoie la liste des éléments actifs. */
GDbItem **g_db_collection_get_last_items(GDbCollection *, size_t *);

/* Evénements concernant les éléments actifs */
typedef enum _ActiveItemChange
{
    AIC_ADDED,                              /* Ajout d'un élément          */
    AIC_REMOVED,                            /* Retrait d'un élément        */
    AIC_UPDATED,                            /* Mise à jour d'un élément    */

} ActiveItemChange;

/* Procède à l'ajout d'un nouvel élément dans la collection. */
bool g_db_collection_add_item(GDbCollection *, GDbItem *);

/* Procède au retrait des éléments désactivés de la collection. */
bool g_db_collection_drop_disabled_items(GDbCollection *, packed_buffer_t *);

/* Procède au retrait d'un élément dans la collection. */
bool g_db_collection_remove_item(GDbCollection *, const GDbItem *);

/* Désactive les éléments en aval d'un horodatage donné. */
bool g_db_collection_disable_at(GDbCollection *, timestamp_t, sqlite3 *, packed_buffer_t *);

/* Prend acte d'un changement d'état d'un élément de collection. */
bool g_db_collection_update_item_state(GDbCollection *, const GDbItem *);



/* --------------------- MANIPULATIONS AVEC UNE BASE DE DONNEES --------------------- */


/* Crée la table d'élément dans une base de données. */
bool g_db_collection_create_db_table(const GDbCollection *, sqlite3 *);

/* Charge un ensemble d'éléments à partir d'une base de données. */
bool g_db_collection_load_all_items(GDbCollection *, sqlite3 *);



/* ------------------- CREATION DE L'ABSTRACTION POUR COLLECTIONS ------------------- */


/* Attache un binaire à une série de collections. */
void attach_binary_to_collections(GList *, GLoadedBinary *);

/* Recherche une collection correspondant à un type donné. */
GDbCollection *find_collection_in_list(GList *, uint32_t);

/* Met à disposition un encadrement des accès aux éléments. */
void lock_unlock_collections(GList *, bool, bool);

#define wlock_collections(lst) lock_unlock_collections(lst, true, true);
#define wunlock_collections(lst) lock_unlock_collections(lst, true, false);

#define rlock_collections(lst) lock_unlock_collections(lst, false, true);
#define runlock_collections(lst) lock_unlock_collections(lst, false, false);

/* Collecte les informations utiles pour un nouvel arrivant. */
bool pack_all_collection_updates(GList *, packed_buffer_t *);

/* Met à jour les statuts d'activité des éléments. */
bool update_activity_in_collections(GList *, packed_buffer_t *, packed_buffer_t *, sqlite3 *);



#endif  /* _ANALYSIS_DB_COLLECTION_H */
