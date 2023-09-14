
/* Chrysalide - Outil d'analyse de fichiers binaires
 * struct.c - définition d'une structure Kaitai
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


#include "type.h"


#include <malloc.h>
#include <string.h>
#include <plugins/yaml/pair.h>


#include "type-int.h"
#include "../parser.h"



/* Initialise la classe des types particuliers pour Kaitai. */
static void g_kaitai_type_class_init(GKaitaiTypeClass *);

/* Initialise un type particulier pour Kaitai. */
static void g_kaitai_type_init(GKaitaiType *);

/* Supprime toutes les références externes. */
static void g_kaitai_type_dispose(GKaitaiType *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_type_finalize(GKaitaiType *);



/* Indique le type défini pour un type particulier pour Kaitai. */
G_DEFINE_TYPE(GKaitaiType, g_kaitai_type, G_TYPE_KAITAI_STRUCT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types particuliers pour Kaitai.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_type_class_init(GKaitaiTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_type_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise un type particulier pour Kaitai.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_type_init(GKaitaiType *type)
{
    type->name = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_type_dispose(GKaitaiType *type)
{
    G_OBJECT_CLASS(g_kaitai_type_parent_class)->dispose(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_type_finalize(GKaitaiType *type)
{
    if (type->name != NULL)
        free(type->name);

    G_OBJECT_CLASS(g_kaitai_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Construit un lecteur de type pour Kaitai.                    *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiType *g_kaitai_type_new(GYamlNode *parent)
{
    GKaitaiType *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_TYPE, NULL);

    if (!g_kaitai_type_create(result, parent))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type   = lecteur de type Kaitai à initialiser pleinement.    *
*                parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Met en place un lecteur de type pour Kaitai.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_type_create(GKaitaiType *type, GYamlNode *parent)
{
    bool result;                            /* Bilan à retourner           */
    const char *name;                       /* Désignation du type         */
    char *sub_path;                         /* Chemin d'accès suivant      */
    GYamlNode *sub;                         /* Contenu Yaml d'un type      */

    result = false;

    /* Extraction du nom */

    if (!G_IS_YAML_PAIR(parent))
        goto exit;

    name = g_yaml_pair_get_key(G_YAML_PAIR(parent));

    type->name = strdup(name);

    /* Extraction des bases du type */

    asprintf(&sub_path, "/%s/", name);
    sub = g_yaml_node_find_first_by_path(parent, sub_path);
    free(sub_path);

    if (sub == NULL)
        goto exit;

    result = g_kaitai_structure_create(G_KAITAI_STRUCT(type), sub);

    g_object_unref(G_OBJECT(sub));

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = définition de type particulier à consulter.           *
*                                                                             *
*  Description : Indique le nom de scène du type représenté.                  *
*                                                                             *
*  Retour      : Désignation humaine.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_type_get_name(const GKaitaiType *type)
{
    const char *result;                     /* Nom à retourner             */

    result = type->name;

    return result;

}
