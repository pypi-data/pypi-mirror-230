
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection-int.h - prototypes et définitions internes pour les collections d'éléments
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


#ifndef _ANALYSIS_DB_COLLECTION_INT_H
#define _ANALYSIS_DB_COLLECTION_INT_H


#include "collection.h"


#include <stdarg.h>



/* Crée la table associée à une collection d'éléments. */
typedef bool (* collec_create_db_table_fc) (const GDbCollection *, sqlite3 *);

/* Charge les valeurs utiles pour une localisation. */
typedef bool (* collec_load_item) (GDbCollection *, const bound_value *, size_t);



/* Collection générique d'éléments (instance) */
struct _GDbCollection
{
    GObject parent;                         /* A laisser en premier        */

    uint32_t featuring;                     /* Fonctionnalité représentée  */
    GType type;                             /* Identifiant GLib équivalent */
    const char *name;                       /* Nom en base de données      */

    /* Référence circulaire */
    GLoadedBinary *binary;                  /* Binaire rattaché éventuel   */

    GDbItem **items;                        /* Eléments rassemblés         */
    size_t count;                           /* Quantité de ces éléments    */
    GHashTable *last_items;                 /* Statuts courants d'éléments */
    GRWLock params_access;                  /* Verrou de protection        */

};

/* Collection générique d'éléments (classe) */
struct _GDbCollectionClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    collec_create_db_table_fc create_table; /* Création de la table en SQL */
    collec_load_item load_item;             /* Charge un élément           */

    /* Signaux */

    void (* content_extended) (GDbCollection *, GDbItem *);

    void (* state_changed) (GDbCollection *, GDbItem *);

    void (* active_changed) (GDbCollection *, ActiveItemChange, GDbItem *);

};



#endif  /* _ANALYSIS_DB_COLLECTION_INT_H */
