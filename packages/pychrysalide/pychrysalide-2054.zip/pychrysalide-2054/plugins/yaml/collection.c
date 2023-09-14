
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection.h - collection de noeuds YAML de type "sequence" ou "mapping"
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


#include "collection.h"


#include <malloc.h>


#include "collection-int.h"



/* -------------------- DEFINITIONS PROPRES POUR LE SUPPORT YAML -------------------- */


/* Initialise la classe des collections de noeuds YAML. */
static void g_yaml_collection_class_init(GYamlCollectionClass *);

/* Initialise une instance de collection de noeuds YAML. */
static void g_yaml_collection_init(GYamlCollection *);

/* Supprime toutes les références externes. */
static void g_yaml_collection_dispose(GYamlCollection *);

/* Procède à la libération totale de la mémoire. */
static void g_yaml_collection_finalize(GYamlCollection *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Recherche le premier noeud correspondant à un chemin. */
static GYamlNode *g_yaml_collection_find_first_by_path(GYamlCollection *, const char *);



/* ---------------------------------------------------------------------------------- */
/*                      DEFINITIONS PROPRES POUR LE SUPPORT YAML                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une collection de noeuds YAML. */
G_DEFINE_TYPE(GYamlCollection, g_yaml_collection, G_TYPE_YAML_NODE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des collections de noeuds YAML.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_collection_class_init(GYamlCollectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GYamlNodeClass *node;                   /* Version parente de classe   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_yaml_collection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_yaml_collection_finalize;

    node = G_YAML_NODE_CLASS(klass);

    node->find = (find_first_yaml_node_fc)g_yaml_collection_find_first_by_path;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de collection de noeuds YAML.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_collection_init(GYamlCollection *collec)
{
    collec->is_seq = false;

    collec->nodes = NULL;
    collec->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_collection_dispose(GYamlCollection *collec)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < collec->count; i++)
        g_clear_object(&collec->nodes[i]);

    G_OBJECT_CLASS(g_yaml_collection_parent_class)->dispose(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_collection_finalize(GYamlCollection *collec)
{
    if (collec->nodes != NULL)
        free(collec->nodes);

    G_OBJECT_CLASS(g_yaml_collection_parent_class)->finalize(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : seq = indique la nature de la future collection.             *
*                                                                             *
*  Description : Construit une collection de noeuds YAML.                     *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlCollection *g_yaml_collection_new(bool seq)
{
    GYamlCollection *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_YAML_COLLEC, NULL);

    if (!g_yaml_collection_create(result, seq))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = noeud d'arborescence YAML à initialiser pleinement. *
*                seq    = indique la nature de la future collection.          *
*                                                                             *
*  Description : Met en place une collection de noeuds YAML.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_yaml_collection_create(GYamlCollection *collec, bool seq)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    collec->is_seq = seq;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = noeud d'arborescence YAML à consulter.              *
*                                                                             *
*  Description : Indique la nature d'une collection YAML.                     *
*                                                                             *
*  Retour      : Nature de la collection.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_yaml_collection_is_sequence(const GYamlCollection *collec)
{
    bool result;                            /* Statut à retourner          */

    result = collec->is_seq;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = collection de noeuds YAML à compléter.              *
*                node   = noeud à rattacher.                                  *
*                                                                             *
*  Description : Ajoute un noeud à une collection de noeuds YAML.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_yaml_collection_add_node(GYamlCollection *collec, GYamlNode *node)
{
    collec->nodes = realloc(collec->nodes, ++collec->count * sizeof(GYamlNode *));

    collec->nodes[collec->count - 1] = node;
    g_object_ref_sink(G_OBJECT(node));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = noeud d'arborescence YAML à consulter.              *
*                count  = taille de la liste constituée. [OUT]                *
*                                                                             *
*  Description : Fournit la liste des noeuds intégrés dans une collection.    *
*                                                                             *
*  Retour      : Enfants d'un noeud issu d'une collection YAML.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlNode **g_yaml_collection_get_nodes(const GYamlCollection *collec, size_t *count)
{
    GYamlNode **result;                     /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours          */

    *count = collec->count;

    result = malloc(*count * sizeof(GYamlNode *));

    for (i = 0; i < *count; i++)
    {
        result[i] = collec->nodes[i];
        g_object_ref(G_OBJECT(result[i]));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = noeud d'arborescence YAML à consulter.              *
*                                                                             *
*  Description : Fournit le premier noeud intégré dans une collection.        *
*                                                                             *
*  Retour      : Noeud issu d'une collection YAML.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlNode *g_yaml_collection_get_first_node(const GYamlCollection *collec)
{
    GYamlNode *result;                      /* Elément à retourner         */

    if (collec->count == 0)
        result = NULL;

    else
    {
        result = collec->nodes[0];
        g_object_ref(G_OBJECT(result));
    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = noeud d'arborescence YAML à consulter.              *
*                path   = chemin d'accès à parcourir.                         *
*                                                                             *
*  Description : Recherche le premier noeud correspondant à un chemin.        *
*                                                                             *
*  Retour      : Noeud avec la correspondance établie ou NULL si non trouvé.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GYamlNode *g_yaml_collection_find_first_by_path(GYamlCollection *collec, const char *path)
{
    GYamlNode *result;                      /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < collec->count && result == NULL; i++)
        result = g_yaml_node_find_first_by_path(collec->nodes[i], path);

    return result;

}
