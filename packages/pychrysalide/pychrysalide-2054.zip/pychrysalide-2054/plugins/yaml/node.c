
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node.c - définition de noeud YAML
 *
 * Copyright (C) 2019-2023 Cyrille Bagard
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


#include "node.h"


#include "node-int.h"



/* Initialise la classe des noeuds d'arborescence YAML. */
static void g_yaml_node_class_init(GYamlNodeClass *);

/* Initialise une instance de noeud d'arborescence YAML. */
static void g_yaml_node_init(GYamlNode *);

/* Supprime toutes les références externes. */
static void g_yaml_node_dispose(GYamlNode *);

/* Procède à la libération totale de la mémoire. */
static void g_yaml_node_finalize(GYamlNode *);



/* Indique le type défini pour un noeud d'arborescence YAML. */
G_DEFINE_TYPE(GYamlNode, g_yaml_node, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des noeuds d'arborescence YAML.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_node_class_init(GYamlNodeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_yaml_node_dispose;
    object->finalize = (GObjectFinalizeFunc)g_yaml_node_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de noeud d'arborescence YAML.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_node_init(GYamlNode *node)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_node_dispose(GYamlNode *node)
{
    G_OBJECT_CLASS(g_yaml_node_parent_class)->dispose(G_OBJECT(node));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_node_finalize(GYamlNode *node)
{
    G_OBJECT_CLASS(g_yaml_node_parent_class)->finalize(G_OBJECT(node));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud d'arborescence YAML à consulter.                *
*                path = chemin d'accès à parcourir.                           *
*                                                                             *
*  Description : Recherche le premier noeud correspondant à un chemin.        *
*                                                                             *
*  Retour      : Noeud avec la correspondance établie ou NULL si non trouvé.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlNode *g_yaml_node_find_first_by_path(GYamlNode *node, const char *path)
{
    GYamlNode *result;                      /* Trouvaille à retourner      */
    GYamlNodeClass *class;                  /* Classe de l'instance        */

    while (path[0] == '/')
        path++;

    if (path[0] == '\0')
    {
        result = node;
        g_object_ref(G_OBJECT(result));
    }
    else
    {
        class = G_YAML_NODE_GET_CLASS(node);

        result = class->find(node, path);

    }

    return result;

}
