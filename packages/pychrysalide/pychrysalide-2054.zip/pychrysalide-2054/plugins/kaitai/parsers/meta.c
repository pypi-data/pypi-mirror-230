
/* Chrysalide - Outil d'analyse de fichiers binaires
 * meta.c - description globale d'une définition Kaitai
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "meta.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <plugins/yaml/pair.h>


#include "meta-int.h"



/* Initialise la classe des descriptions globales Kaitai. */
static void g_kaitai_meta_class_init(GKaitaiMetaClass *);

/* Initialise une description globale de définition Kaitai. */
static void g_kaitai_meta_init(GKaitaiMeta *);

/* Supprime toutes les références externes. */
static void g_kaitai_meta_dispose(GKaitaiMeta *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_meta_finalize(GKaitaiMeta *);



/* Indique le type défini pour une description globale Kaitai. */
G_DEFINE_TYPE(GKaitaiMeta, g_kaitai_meta, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des descriptions globales Kaitai.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_meta_class_init(GKaitaiMetaClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_meta_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_meta_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une description globale de définition Kaitai.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_meta_init(GKaitaiMeta *meta)
{
    meta->id = NULL;
    meta->title = NULL;

    meta->endian = SRE_LITTLE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_meta_dispose(GKaitaiMeta *meta)
{
    G_OBJECT_CLASS(g_kaitai_meta_parent_class)->dispose(G_OBJECT(meta));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_meta_finalize(GKaitaiMeta *meta)
{
    if (meta->id != NULL)
        free(meta->id);

    if (meta->title != NULL)
        free(meta->title);

    G_OBJECT_CLASS(g_kaitai_meta_parent_class)->finalize(G_OBJECT(meta));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Construit une description globale Kaitai.                    *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiMeta *g_kaitai_meta_new(GYamlNode *parent)
{
    GKaitaiMeta *result;                   /* Identifiant à retourner     */

    result = g_object_new(G_TYPE_KAITAI_META, NULL);

    if (!g_kaitai_meta_create(result, parent))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta   = description globale à initialiser pleinement.       *
*                parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Met en place une description globale Kaitai.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_meta_create(GKaitaiMeta *meta, GYamlNode *parent)
{
    bool result;                            /* Bilan à retourner           */
    GYamlNode *node;                        /* Noeud particulier présent   */
    const char *value;                      /* Valeur Yaml particulière    */

    result = true;

    /* Identifiant */

    node = g_yaml_node_find_first_by_path(parent, "/meta/id");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
            meta->id = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Titre */

    node = g_yaml_node_find_first_by_path(parent, "/meta/title");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
            meta->title = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Boutisme */

    node = g_yaml_node_find_first_by_path(parent, "/meta/endian");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (strcmp(value, "le") == 0)
            meta->endian = SRE_LITTLE;

        else if (strcmp(value, "be") == 0)
            meta->endian = SRE_BIG;

        g_object_unref(G_OBJECT(node));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta = description globale à consulter.                      *
*                                                                             *
*  Description : Fournit l'identifié associé à une définiton Kaitai.          *
*                                                                             *
*  Retour      : Identifiant de définition complète ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_meta_get_id(const GKaitaiMeta *meta)
{
    const char *result;                     /* Chaîne à retourner          */

    result = meta->id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta = description globale à consulter.                      *
*                                                                             *
*  Description : Fournit la désignation humaine d'une définiton Kaitai.       *
*                                                                             *
*  Retour      : Intitulé de définition OU NULL.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_meta_get_title(const GKaitaiMeta *meta)
{
    const char *result;                     /* Chaîne à retourner          */

    result = meta->title;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : meta = description globale à consulter.                      *
*                                                                             *
*  Description : Indique le boustime observé par défaut par une définiton.    *
*                                                                             *
*  Retour      : Boustime, petit par défaut.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SourceEndian g_kaitai_meta_get_endian(const GKaitaiMeta *meta)
{
    SourceEndian result;                    /* Chaîne à retourner          */

    result = meta->endian;

    return result;

}
