
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.c - lecteur de contenu Yaml
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


#include "parser.h"


#include <assert.h>
#include <malloc.h>
#include <yaml.h>
#include <gio/gio.h>


#include <analysis/contents/file.h>


#include "collection.h"
#include "pair.h"


#define SCALAR_STYLE_TO_ORIGINAL_STYLE(v)               \
    ({                                                  \
        YamlOriginalStyle __result;                     \
        if (v == YAML_SINGLE_QUOTED_SCALAR_STYLE)       \
            __result = YOS_SINGLE_QUOTED;               \
        else if (v == YAML_DOUBLE_QUOTED_SCALAR_STYLE)  \
            __result = YOS_DOUBLE_QUOTED;               \
        else                                            \
            __result = YOS_PLAIN;                       \
        __result;                                       \
    })


/* Construit la version GLib d'un noeud YAML brut. */
static GYamlPair *build_pair_from_yaml(yaml_document_t *, int, int);

/* Transforme un noeud YAML brut en sa version Glib. */
static GYamlNode *translate_yaml_node(yaml_document_t *, yaml_node_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : document = gestionnaire de l'ensemble des noeuds bruts.      *
*                key      = indice de la clef du noeud à convertir.           *
*                value    = indice de la valeur du noeud à convertir.         *
*                                                                             *
*  Description : Construit la version GLib d'un noeud YAML brut.              *
*                                                                             *
*  Retour      : Noeud GLib obtenu ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GYamlPair *build_pair_from_yaml(yaml_document_t *document, int key, int value)
{
    GYamlPair *result;                      /* Racine à retourner          */
    yaml_node_t *key_node;                  /* Noeud brut de la clef       */
    yaml_node_t *value_node;                /* Noeud brut de la valeur     */
    GYamlNode *children;                    /* Collection de noeuds YAML   */

    result = NULL;

    key_node = yaml_document_get_node(document, key);
    assert(key_node != NULL);

    if (key_node->type != YAML_SCALAR_NODE)
        goto exit;

    value_node = yaml_document_get_node(document, value);
    assert(value_node != NULL);

    if (value_node->type == YAML_SCALAR_NODE)
        result = g_yaml_pair_new((char *)key_node->data.scalar.value,
                                 SCALAR_STYLE_TO_ORIGINAL_STYLE(key_node->data.scalar.style),
                                 (char *)value_node->data.scalar.value,
                                 SCALAR_STYLE_TO_ORIGINAL_STYLE(value_node->data.scalar.style));

    else
    {
        children = translate_yaml_node(document, value_node);

        if (children != NULL)
        {
            result = g_yaml_pair_new((char *)key_node->data.scalar.value,
                                     SCALAR_STYLE_TO_ORIGINAL_STYLE(key_node->data.scalar.style),
                                     NULL, YOS_PLAIN);

            g_yaml_pair_set_children(result, G_YAML_COLLEC(children));

        }

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : document = gestionnaire de l'ensemble des noeuds bruts.      *
*                node     = point de départ des transformations.              *
*                                                                             *
*  Description : Transforme un noeud YAML brut en sa version Glib.            *
*                                                                             *
*  Retour      : Noeud GLib obtenu ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GYamlNode *translate_yaml_node(yaml_document_t *document, yaml_node_t *node)
{
    GYamlNode *result;                      /* Racine à retourner          */
    yaml_node_item_t *index;                /* Elément d'une série         */
    yaml_node_t *item;                      /* Elément d'une série         */
    GYamlNode *child;                       /* Version GLib de l'élément   */
    yaml_node_pair_t *pair;                 /* Combinaison clef/valeur     */
    GYamlPair *sub;                         /* Sous-noeud à intégrer       */

    switch (node->type)
    {
        case YAML_SCALAR_NODE:
            result = G_YAML_NODE(g_yaml_pair_new((char *)node->data.scalar.value,
                                                 SCALAR_STYLE_TO_ORIGINAL_STYLE(node->data.scalar.style),
                                                 NULL, YOS_PLAIN));
            break;

        case YAML_SEQUENCE_NODE:

            result = G_YAML_NODE(g_yaml_collection_new(true));

            for (index = node->data.sequence.items.start; index < node->data.sequence.items.top; index++)
            {
                item = yaml_document_get_node(document, *index);
                assert(item != NULL);

                child = translate_yaml_node(document, item);

                if (child == NULL)
                {
                    g_clear_object(&result);
                    break;
                }

                g_yaml_collection_add_node(G_YAML_COLLEC(result), child);

            }

            break;

        case YAML_MAPPING_NODE:

            result = G_YAML_NODE(g_yaml_collection_new(false));

            for (pair = node->data.mapping.pairs.start; pair < node->data.mapping.pairs.top; pair++)
            {
                sub = build_pair_from_yaml(document, pair->key, pair->value);

                if (sub == NULL)
                {
                    g_clear_object(&result);
                    break;
                }

                g_yaml_collection_add_node(G_YAML_COLLEC(result), G_YAML_NODE(sub));

            }

            break;

        default:
            assert(false);
            result = NULL;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : text = définitions textuelles d'un contenu brut.             *
*                len  = taille de ces définitions.                            *
*                                                                             *
*  Description : Crée une arborescence YAML pour contenu au format adapté.    *
*                                                                             *
*  Retour      : Arborescence YAML mise en place ou NULL en cas d'échec.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlNode *parse_yaml_from_text(const char *text, size_t len)
{
    GYamlNode *result;                      /* Racine à retourner          */
    yaml_parser_t parser;                   /* Lecteur du contenu fourni   */
    yaml_document_t document;               /* Document YAML constitué     */
    int ret;                                /* Bilan de la constitution    */
    yaml_node_t *root;                      /* Elément racine brut         */

    result = NULL;

    yaml_parser_initialize(&parser);

    yaml_parser_set_input_string(&parser, (const unsigned char *)text, len);

    ret = yaml_parser_load(&parser, &document);
    if (ret != 1) goto bad_loading;

    root = yaml_document_get_root_node(&document);

    if (root != NULL)
        result = translate_yaml_node(&document, root);

    yaml_document_delete(&document);

 bad_loading:

    yaml_parser_delete(&parser);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin vers des définitions de règles.            *
*                                                                             *
*  Description : Crée une arborescence YAML pour fichier au format adapté.    *
*                                                                             *
*  Retour      : Arborescence YAML mise en place ou NULL en cas d'échec.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GYamlNode *parse_yaml_from_file(const char *filename)
{
    GYamlNode *result;                      /* Racine à retourner          */
    GBinContent *content;                   /* Fichier à parcourir         */
    phys_t size;                            /* Taille du contenu associé   */
    vmpa2t start;                           /* Tête de lecture             */
    const bin_t *data;                      /* Données à consulter         */
    char *dumped;                           /* Contenu manipulable         */

    result = NULL;

    content = g_file_content_new(filename);
    if (content == NULL) goto no_content;

    size = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &start);
    data = g_binary_content_get_raw_access(content, &start, size);

    dumped = malloc((size + 1) * sizeof(char));

    memcpy(dumped, data, size);
    dumped[size] = '\0';

    result = parse_yaml_from_text(dumped, size);

    free(dumped);

    g_object_unref(G_OBJECT(content));

 no_content:

    return result;

}
