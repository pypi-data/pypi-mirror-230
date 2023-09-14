
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pair.c - noeud YAML de paire clef/valeur
 *
 * Copyright (C) 2020-2023 Cyrille Bagard
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


#include "pair.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <common/extstr.h>


#include "pair-int.h"



/* -------------------- DEFINITIONS PROPRES POUR LE SUPPORT YAML -------------------- */


/* Initialise la classe des noeuds d'arborescence YAML. */
static void g_yaml_pair_class_init(GYamlPairClass *);

/* Initialise une instance de noeud d'arborescence YAML. */
static void g_yaml_pair_init(GYamlPair *);

/* Supprime toutes les références externes. */
static void g_yaml_pair_dispose(GYamlPair *);

/* Procède à la libération totale de la mémoire. */
static void g_yaml_pair_finalize(GYamlPair *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Recherche le premier noeud correspondant à un chemin. */
static GYamlNode *g_yaml_pair_find_first_by_path(GYamlPair *, const char *);



/* ---------------------------------------------------------------------------------- */
/*                      DEFINITIONS PROPRES POUR LE SUPPORT YAML                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un noeud d'arborescence YAML. */
G_DEFINE_TYPE(GYamlPair, g_yaml_pair, G_TYPE_YAML_NODE);


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

static void g_yaml_pair_class_init(GYamlPairClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GYamlNodeClass *node;                   /* Version parente de classe   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_yaml_pair_dispose;
    object->finalize = (GObjectFinalizeFunc)g_yaml_pair_finalize;

    node = G_YAML_NODE_CLASS(klass);

    node->find = (find_first_yaml_node_fc)g_yaml_pair_find_first_by_path;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de noeud d'arborescence YAML.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_pair_init(GYamlPair *pair)
{
    pair->key = NULL;
    pair->key_style = YOS_PLAIN;

    pair->value = NULL;
    pair->value_style = YOS_PLAIN;

    pair->children = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_pair_dispose(GYamlPair *pair)
{
    g_clear_object(&pair->children);

    G_OBJECT_CLASS(g_yaml_pair_parent_class)->dispose(G_OBJECT(pair));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_yaml_pair_finalize(GYamlPair *pair)
{
    if (pair->key != NULL)
        free(pair->key);

    if (pair->value != NULL)
        free(pair->value);

    G_OBJECT_CLASS(g_yaml_pair_parent_class)->finalize(G_OBJECT(pair));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key    = désignation pour le noeud YAML.                     *
*                kstyle = format d'origine de la clef.                        *
*                value  = éventuelle valeur directe portée par le noeud.      *
*                vstyle = éventuel format d'origine de l'éventuelle valeur.   *
*                                                                             *
*  Description : Construit un noeud d'arborescence YAML.                      *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlPair *g_yaml_pair_new(const char *key, YamlOriginalStyle kstyle, const char *value, YamlOriginalStyle vstyle)
{
    GYamlPair *result;                      /* Structure à retourner       */

    result = g_object_new(G_TYPE_YAML_PAIR, NULL);

    if (!g_yaml_pair_create(result, key, kstyle, value, vstyle))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair   = paire YAML à initialiser pleinement.                *
*                key    = désignation pour le noeud YAML.                     *
*                kstyle = format d'origine de la clef.                        *
*                value  = éventuelle valeur directe portée par le noeud.      *
*                vstyle = éventuel format d'origine de l'éventuelle valeur.   *
*                                                                             *
*  Description : Met en place une pair clef/valeur YAML.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_yaml_pair_create(GYamlPair *pair, const char *key, YamlOriginalStyle kstyle, const char *value, YamlOriginalStyle vstyle)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    pair->key = strdup(key);
    pair->key_style = kstyle;

    if (value != NULL)
    {
        pair->value = strdup(value);
        pair->value_style = vstyle;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                                                                             *
*  Description : Fournit la clef représentée dans une paire en YAML.          *
*                                                                             *
*  Retour      : Clef sous forme de chaîne de caractères.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_yaml_pair_get_key(const GYamlPair *pair)
{
    char *result;                           /* Valeur à retourner          */

    result = pair->key;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                                                                             *
*  Description : Indique le format d'origine YAML associé à la clef.          *
*                                                                             *
*  Retour      : Valeur renseignée lors du chargement du noeud.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

YamlOriginalStyle g_yaml_pair_get_key_style(const GYamlPair *pair)
{
    YamlOriginalStyle result;               /* Indication à retourner      */

    result = pair->key_style;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                                                                             *
*  Description : Fournit l'éventuelle valeur d'une paire en YAML.             *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_yaml_pair_get_value(const GYamlPair *pair)
{
    char *result;                           /* Valeur à retourner          */

    result = pair->value;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                                                                             *
*  Description : Indique le format d'origine YAML associé à la valeur.        *
*                                                                             *
*  Retour      : Valeur renseignée lors du chargement du noeud.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

YamlOriginalStyle g_yaml_pair_get_value_style(const GYamlPair *pair)
{
    YamlOriginalStyle result;               /* Indication à retourner      */

    result = pair->value_style;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                                                                             *
*  Description : Rassemble une éventuelle séquence de valeurs attachées.      *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_yaml_pair_aggregate_value(const GYamlPair *pair)
{
    char *result;                           /* Valeur à retourner          */
    GYamlNode **nodes;                      /* Eventuels noeuds trouvés    */
    size_t count;                           /* Quantité de ces noeuds      */
    size_t i;                               /* Boucle de parcours          */
    GYamlPair *child;                       /* Couple clef/valeur enfant   */
    bool failed;                            /* Détection d'un échec        */

    result = NULL;

    if (pair->value != NULL)
        result = strdup(pair->value);

    else if (pair->children != NULL)
    {
        if (!g_yaml_collection_is_sequence(pair->children))
            goto exit;

        nodes = g_yaml_collection_get_nodes(pair->children, &count);

        if (count == 0)
            result = strdup("[ ]");

        else
        {
            result = strdup("[ ");

            for (i = 0; i < count; i++)
            {
                if (!G_IS_YAML_PAIR(nodes[i]))
                    break;

                child = G_YAML_PAIR(nodes[i]);

                if (child->value != NULL)
                    break;

                if (i > 0)
                    result = stradd(result, ", ");

                switch (child->key_style)
                {
                    case YOS_PLAIN:
                        result = stradd(result, child->key);
                        break;

                    case YOS_SINGLE_QUOTED:
                        result = straddfmt(result, "'%s'", child->key);
                        break;

                    case YOS_DOUBLE_QUOTED:
                        result = straddfmt(result, "\"%s\"", child->key);
                        break;

                }

                g_object_unref(G_OBJECT(nodes[i]));

            }

            failed = (i < count);

            for (; i < count; i++)
                g_object_unref(G_OBJECT(nodes[i]));

            free(nodes);

            if (failed)
            {
                free(result);
                result = NULL;
            }

            else
                result = stradd(result, " ]");

        }

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair     = noeud d'arborescence YAML à compléter.            *
*                children = collection de noeuds YAML.                        *
*                                                                             *
*  Description : Attache une collection de noeuds YAML à un noeud.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_yaml_pair_set_children(GYamlPair *pair, GYamlCollection *children)
{
    g_clear_object(&pair->children);

    g_object_ref_sink(G_OBJECT(children));
    pair->children = children;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                                                                             *
*  Description : Fournit une éventuelle collection rattachée à un noeud.      *
*                                                                             *
*  Retour      : Collection de noeuds YAML ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlCollection *g_yaml_pair_get_children(const GYamlPair *pair)
{
    GYamlCollection *result;                /* Collection à renvoyer       */

    result = pair->children;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : pair = noeud d'arborescence YAML à consulter.                *
*                path = chemin d'accès à parcourir.                           *
*                                                                             *
*  Description : Recherche le premier noeud correspondant à un chemin.        *
*                                                                             *
*  Retour      : Noeud avec la correspondance établie ou NULL si non trouvé.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GYamlNode *g_yaml_pair_find_first_by_path(GYamlPair *pair, const char *path)
{
    GYamlNode *result;                      /* Trouvaille à retourner      */
    char *next;                             /* Prochaine partie du chemin  */
    size_t cmplen;                          /* Etendue de la comparaison   */
    int ret;                                /* Bilan d'une comparaison     */

    assert(path[0] != '/' && path[0] != '\0');

    /* Correspondance au niveau du noeud ? */

    next = strchr(path, '/');

    if (next == NULL)
        ret = strcmp(path, pair->key);

    else
    {
        cmplen = next - path;
        assert(cmplen > 0);

        ret = strncmp(path, pair->key, cmplen);

    }

    /* Si correspondance il y a... */

    if (ret == 0)
    {
        /* ...  et que la recherche se trouve en bout de parcours */
        if (next == NULL)
        {
            result = G_YAML_NODE(pair);
            g_object_ref(G_OBJECT(result));
        }

        /* Recherche supplémentaire dans les sous-noeuds ? */

        else if (pair->children != NULL)
            result = g_yaml_node_find_first_by_path(G_YAML_NODE(pair->children), path + cmplen);

        else
            result = NULL;

    }

    else
        result = NULL;

    return result;

}
