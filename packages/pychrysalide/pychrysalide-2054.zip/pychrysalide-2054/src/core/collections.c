
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collections.c - enregistrement et la diffusion des collections
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


#include "collections.h"


#include <assert.h>
#include <malloc.h>
#include <pthread.h>


#include "../analysis/db/collection.h"
#include "../analysis/db/protocol.h"
#include "../analysis/db/items/bookmark.h"
#include "../analysis/db/items/comment.h"
#include "../analysis/db/items/move.h"
#include "../analysis/db/items/switcher.h"



/* Mémorisation des types de collection enregistrés */
static GType *_collection_definitions = NULL;
static uint32_t _collection_definitions_count = 0;

/* Verrou pour des accès atomiques */
G_LOCK_DEFINE_STATIC(_collec_mutex);



/******************************************************************************
*                                                                             *
*  Paramètres  : items = type GLib des éléments constituant une collection.   *
*                                                                             *
*  Description : Enregistre un type d'élément à gérer par collection.         *
*                                                                             *
*  Retour      : Identifiant unique attribué "dynamiquement".                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t register_collection_type(GType items)
{
    uint32_t result;                        /* Identifiant à retourner     */

    G_LOCK(_collec_mutex);

    result = _collection_definitions_count++;

    _collection_definitions = (GType *)realloc(_collection_definitions,
                                               _collection_definitions_count * sizeof(GType));

    _collection_definitions[result] = items;

    G_UNLOCK(_collec_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Charge les définitions de collections "natives".             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_hard_coded_collection_definitions(void)
{
#ifndef NDEBUG
    uint32_t id;                            /* Identifiant unique retourné */
#endif

    /**
     * La liste des chargements doit se faire dans le même ordre que
     * la définition de l'énumération 'DBFeatures' dans le fichier 'protocol.h',
     * afin de garder la correspondance entre les identifiants.
     */

#if 0 //ndef NDEBUG
#   define REGISTER_COLLECTION(tp, exp)     \
    id = register_collection_type(tp);      \
    assert(id == exp);
#else
#   define REGISTER_COLLECTION(tp, exp)     \
        register_collection_type(tp);
#endif

    REGISTER_COLLECTION(G_TYPE_BM_COLLECTION, DBF_BOOKMARKS);

    REGISTER_COLLECTION(G_TYPE_COMMENT_COLLECTION, DBF_COMMENTS);

    //REGISTER_COLLECTION(G_TYPE_MOVE_COLLECTION, DBF_MOVES);

    REGISTER_COLLECTION(G_TYPE_SWITCHER_COLLECTION, DBF_DISPLAY_SWITCHERS);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge toutes les définitions de collections.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_collection_definitions(void)
{
    if (_collection_definitions != NULL)
        free(_collection_definitions);

    _collection_definitions = NULL;
    _collection_definitions_count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Construit un nouvel ensemble de collections.                 *
*                                                                             *
*  Retour      : Liste complète de collections vierges.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GList *create_collections_list(void)
{
    GList *result;                          /* Groupe à retourner          */
    uint32_t i;                             /* Boucle de parcours          */
    GDbCollection *collec;                  /* Nouveau groupe à intégrer   */

    result = NULL;

    G_LOCK(_collec_mutex);

    for (i = 0; i < _collection_definitions_count; i++)
    {
        collec = g_object_new(_collection_definitions[i], NULL);

        result = g_list_append(result, collec);

    }

    G_UNLOCK(_collec_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = liste complète de collections à traiter. [OUT]      *
*                                                                             *
*  Description : Détruit un ensemble de collections.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_collections_list(GList **collec)
{
    if (*collec != NULL)
    {
        g_list_free_full(*collec, g_object_unref);

        *collec = NULL;

    }

}
