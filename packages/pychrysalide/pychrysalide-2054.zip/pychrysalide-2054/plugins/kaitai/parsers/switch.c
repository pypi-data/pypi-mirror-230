
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switch.h - gestion des énumérations Kaitai
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


#include "switch.h"


#include <assert.h>
#include <errno.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include <common/extstr.h>
#include <common/sort.h>
#include <core/logs.h>
#include <plugins/yaml/pair.h>


#include "switch-int.h"
#include "../expression.h"



/* ------------------------ BASCULE DYNAMIQUE SELON CONTEXTE ------------------------ */


/* Construit une valeur d'énumération à partir d'indications. */
static switch_case_t *build_switch_case(const GYamlNode *, bool *);

/* Supprime de la mémoire une bascule selon contexte. */
static void delete_switch_case(switch_case_t *);

/* Détermine si le cas correspond à une valeur de bascule. */
static const char *is_suitable_switch_case_for_bytes(const switch_case_t *, const resolved_value_t *);

/* Détermine si le cas correspond à une valeur de bascule. */
static const char *is_suitable_switch_case_for_integer(const switch_case_t *, kaitai_scope_t *, const resolved_value_t *);



/* ----------------------- SELECTION DYNAMIQUE DE TYPE KAITAI ----------------------- */


/* Initialise la classe des sélections dynamiques de types. */
static void g_kaitai_switch_class_init(GKaitaiSwitchClass *);

/* Initialise une sélection dynamique de type Kaitai. */
static void g_kaitai_switch_init(GKaitaiSwitch *);

/* Supprime toutes les références externes. */
static void g_kaitai_switch_dispose(GKaitaiSwitch *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_switch_finalize(GKaitaiSwitch *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt un contenu binaire selon des spécifications Kaitai. */
static bool g_kaitai_switch_parse_content(GKaitaiSwitch *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);



/* ---------------------------------------------------------------------------------- */
/*                          BASCULE DYNAMIQUE SELON CONTEXTE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = noeud Yaml à venir lire.                           *
*                defcase = indique si une valeur par défaut est visée. [OUT]  *
*                                                                             *
*  Description : Construit une valeur d'énumération à partir d'indications.   *
*                                                                             *
*  Retour      : Structure de valeur mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static switch_case_t *build_switch_case(const GYamlNode *node, bool *defcase)
{
    switch_case_t *result;                  /* Enregistrement à retourner  */
    const char *key;                        /* Clef d'une conversion       */
    const char *value;                      /* Valeur Yaml particulière    */

    result = NULL;

    if (!G_IS_YAML_PAIR(node))
        goto exit;

    key = g_yaml_pair_get_key(G_YAML_PAIR(node));
    value = g_yaml_pair_get_value(G_YAML_PAIR(node));

    if (value == NULL)
        goto exit;

    result = malloc(sizeof(switch_case_t));

    result->value = strdup(key);
    result->type = strdup(value);

    *defcase = (strcmp(key, "_") == 0);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : swcase = valeur à traiter.                                   *
*                                                                             *
*  Description : Supprime de la mémoire une bascule selon contexte.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
*****************************************************************************/

static void delete_switch_case(switch_case_t *swcase)
{
    free(swcase->value);

    free(swcase->type);

    free(swcase);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : swcase = valeur à analyser.                                  *
*                value  = valeur à comparer.                                  *
*                                                                             *
*  Description : Détermine si le cas correspond à une valeur de bascule.      *
*                                                                             *
*  Retour      : Type à utiliser ou NULL si aucune correspondance établie.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
*****************************************************************************/

static const char *is_suitable_switch_case_for_bytes(const switch_case_t *swcase, const resolved_value_t *value)
{
    const char *result;                     /* Désignation à retourner     */
    sized_string_t key;                     /* Changement de format        */
    bool valid;                             /* Validité des opérations     */
    int ret;                                /* Bilan d'une comparaison     */

    result = NULL;

    key.data = swcase->value;
    key.len = strlen(swcase->value);

    valid = (key.len > 2);

    if (valid)
        valid = (swcase->value[0] == '"' || swcase->value[0] == '\'');

    if (valid)
    {
        valid = (key.data[0] == key.data[key.len - 1]);

        key.data++;
        key.len -= 2;

    }

    if (valid)
    {
        if (value->type == GVT_BYTES)
        {
            ret = szmemcmp(&key, &value->bytes);

            if (ret == 0)
                result = swcase->type;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : swcase = valeur à analyser.                                  *
*                locals = variables locales pour les résolutions de types.    *
*                value  = valeur à comparer.                                  *
*                                                                             *
*  Description : Détermine si le cas correspond à une valeur de bascule.      *
*                                                                             *
*  Retour      : Type à utiliser ou NULL si aucune correspondance établie.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
*****************************************************************************/

static const char *is_suitable_switch_case_for_integer(const switch_case_t *swcase, kaitai_scope_t *locals, const resolved_value_t *value)
{
    const char *result;                     /* Désignation à retourner     */
    bool valid;                             /* Validité des opérations     */
    resolved_value_t key;                   /* Changement de format        */
    unsigned long long unsigned_conv;       /* Valeur convertie #1         */
    long long signed_conv;                  /* Valeur convertie #2         */

    result = NULL;

    valid = (swcase->value[0] != '"' && swcase->value[0] != '\'');

    if (valid)
    {
        if (strchr(swcase->value, ':') != NULL)
        {
            valid = resolve_kaitai_expression_as_integer(locals, swcase->value, strlen(swcase->value), &key);

            if (valid)
            {
                if (key.type == GVT_UNSIGNED_INTEGER)
                {
                    if (value->type == GVT_UNSIGNED_INTEGER)
                    {
                        if (key.unsigned_integer == value->unsigned_integer)
                            result = swcase->type;
                    }
                    else
                    {
                        if (key.unsigned_integer == value->signed_integer)
                            result = swcase->type;
                    }
                }
                else
                {
                    if (value->type == GVT_UNSIGNED_INTEGER)
                    {
                        if (key.signed_integer == value->unsigned_integer)
                            result = swcase->type;
                    }
                    else
                    {
                        if (key.signed_integer == value->signed_integer)
                            result = swcase->type;
                    }
                }

            }

        }

        else
        {
            if (value->type == GVT_UNSIGNED_INTEGER)
            {
                unsigned_conv = strtoull(swcase->value, NULL, 10);

                valid = (errno != ERANGE && errno != EINVAL);

                if (valid && unsigned_conv == value->unsigned_integer)
                    result = swcase->type;

            }
            else
            {
                signed_conv = strtoll(swcase->value, NULL, 10);

                valid = (errno != ERANGE && errno != EINVAL);

                if (valid && signed_conv == value->signed_integer)
                    result = swcase->type;

            }

        }

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         SELECTION DYNAMIQUE DE TYPE KAITAI                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un choix dynamique de type Kaitai. */
G_DEFINE_TYPE(GKaitaiSwitch, g_kaitai_switch, G_TYPE_KAITAI_PARSER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des sélections dynamiques de types.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_switch_class_init(GKaitaiSwitchClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKaitaiParserClass *parser;             /* Version parente de la classe*/ 

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_switch_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_switch_finalize;

    parser = G_KAITAI_PARSER_CLASS(klass);

    parser->parse = (parse_kaitai_fc)g_kaitai_switch_parse_content;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kswitch = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une sélection dynamique de type Kaitai.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_switch_init(GKaitaiSwitch *kswitch)
{
    kswitch->target = NULL;

    kswitch->cases = NULL;
    kswitch->count = 0;

    kswitch->defcase = NULL;

    kswitch->generic = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kswitch = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_switch_dispose(GKaitaiSwitch *kswitch)
{
    g_clear_object(&kswitch->generic);

    G_OBJECT_CLASS(g_kaitai_switch_parent_class)->dispose(G_OBJECT(kswitch));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kswitch = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_switch_finalize(GKaitaiSwitch *kswitch)
{
    size_t i;                               /* Boucle de parcours          */

    if (kswitch->target != NULL)
        free(kswitch->target);

    for (i = 0; i < kswitch->count; i++)
        delete_switch_case(kswitch->cases[i]);

    if (kswitch->cases != NULL)
        free(kswitch->cases);

    if (kswitch->defcase != NULL)
        delete_switch_case(kswitch->defcase);

    G_OBJECT_CLASS(g_kaitai_switch_parent_class)->finalize(G_OBJECT(kswitch));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent  = noeud Yaml contenant l'attribut à constituer.      *
*                generic = lecteur d'attribut Kaitai à dériver.               *
*                                                                             *
*  Description : Construit une sélection dynamique de type Kaitai.            *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiSwitch *g_kaitai_switch_new(GYamlNode *parent, GKaitaiAttribute *generic)
{
    GKaitaiSwitch *result;                   /* Identifiant à retourner     */

    result = g_object_new(G_TYPE_KAITAI_SWITCH, NULL);

    if (!g_kaitai_switch_create(result, parent, generic))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kswitch = sélectionneur de type  à initialiser pleinement.   *
*                parent  = noeud Yaml contenant l'attribut à constituer.      *
*                generic = lecteur d'attribut Kaitai à dériver.               *
*                                                                             *
*  Description : Met en place une sélection dynamique de type Kaitai.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_switch_create(GKaitaiSwitch *kswitch, GYamlNode *parent, GKaitaiAttribute *generic)
{
    bool result;                            /* Bilan à retourner           */
    GYamlNode *node;                        /* Noeud de définition         */
    GYamlNode *subnode;                     /* Noeud de précisions         */
    const char *value;                      /* Valeur Yaml particulière    */
    GYamlNode *collec;                      /* Liste de noeuds à traiter   */
    GYamlNode **subnodes;                   /* Eventuels noeuds trouvés    */
    size_t count;                           /* Quantité de ces noeuds      */
    size_t i;                               /* Boucle de parcours          */
    bool defcase;                           /* Définition par défaut ?     */
    switch_case_t *swcase;                  /* Bascule à noter             */

    result = false;

    node = g_yaml_node_find_first_by_path(parent, "/type/");
    if (node == NULL) goto exit;

    /* Source de la bascule */

    subnode = g_yaml_node_find_first_by_path(node, "/switch-on");
    assert(G_IS_YAML_PAIR(subnode));

    value = g_yaml_pair_get_value(G_YAML_PAIR(subnode));
    if (value == NULL)
    {
        g_object_unref(G_OBJECT(subnode));
        goto bad_definition;
    }

    kswitch->target = strdup(value);

    g_object_unref(G_OBJECT(subnode));

    /* Conditions de bascule */

    collec = g_yaml_node_find_first_by_path(node, "/cases/");
    if (collec == NULL) goto bad_definition;
    if (!G_IS_YAML_COLLEC(collec)) goto bad_definition;

    subnodes = g_yaml_collection_get_nodes(G_YAML_COLLEC(collec), &count);

    g_object_unref(G_OBJECT(collec));

    if (count == 0) goto bad_definition;

    for (i = 0; i < count; i++)
    {
        swcase = build_switch_case(subnodes[i], &defcase);
        if (swcase == NULL) break;

        g_object_unref(G_OBJECT(subnodes[i]));

        kswitch->cases = realloc(kswitch->cases, ++kswitch->count * sizeof(switch_case_t *));
        kswitch->cases[kswitch->count - 1] = swcase;

    }

    result = (i == count);

    for (; i < count; i++)
        g_object_unref(G_OBJECT(subnodes[i]));

    if (subnodes != NULL)
        free(subnodes);

    /* Fin des procédures */

    if (result)
    {
        kswitch->generic = generic;
        g_object_ref(G_OBJECT(generic));
    }

 bad_definition:

    g_object_unref(G_OBJECT(node));

 exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : kswitch = structure Kaitai en cours de parcours.             *
*                locals  = variables locales pour les résolutions de types.   *
*                content = données binaires à analyser et traduire.           *
*                pos     = tête de lecture courante. [OUT]                    *
*                record  = noeud d'arborescence d'éléments rencontrés. [OUT]  *
*                                                                             *
*  Description : Parcourt un contenu binaire selon des spécifications Kaitai. *
*                                                                             *
*  Retour      : Bilan de l'opératon : true pour continuer, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_kaitai_switch_parse_content(GKaitaiSwitch *kswitch, kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    GMatchRecord *reference;                /* Correspondance à utiliser   */
    GKaitaiParser *creator;                 /* Lecteur d'origine           */
    KaitaiAttributePayload payload;         /* Type de charge supportée    */
    BaseType basic;                         /* Type de base reconnu        */
    bool is_string;                         /* Type lié à une chaîne ?     */
#ifndef NDEBUG
    bool status;                            /* Bilan d'une consultation    */
#endif
    const char *final_type;                 /* Type à utiliser au final    */
    resolved_value_t value;                 /* Valeur de cible entière     */
    size_t i;                               /* Boucle de parcours          */
    GKaitaiAttribute *attrib;               /* Lecteur approprié           */

    result = false;

    /* Détermination de la forme de comparaison */

    reference = g_match_record_find_by_name(locals->parent,
                                            kswitch->target, strlen(kswitch->target),
                                            DIRECT_SEARCH_DEEP_LEVEL);

    if (reference == NULL)
        goto exit;

    creator = g_match_record_get_creator(reference);

    if (creator == NULL)
        goto exit_with_ref;

    if (!G_IS_KAITAI_ATTRIBUTE(creator))
        goto exit_with_creator;

    payload = g_kaitai_attribute_get_payload(G_KAITAI_ATTRIBUTE(creator));

    if ((payload & KAP_BASIC_TYPE) == 0)
        goto exit_with_creator;

#ifndef NDEBUG
    status = g_kaitai_attribute_get_basic_type(G_KAITAI_ATTRIBUTE(creator), &basic, &is_string);
    assert(status);
#else
    g_kaitai_attribute_get_basic_type(G_KAITAI_ATTRIBUTE(creator), &basic, &is_string);
#endif

    /* Détermination du type visé */

    final_type = NULL;

    if (is_string)
    {
        result = resolve_kaitai_expression_as_bytes(locals,
                                                    kswitch->target,
                                                    strlen(kswitch->target),
                                                    &value);
        if (!result) goto exit_with_creator;

        for (i = 0; i < kswitch->count; i++)
        {
            final_type = is_suitable_switch_case_for_bytes(kswitch->cases[i], &value);

            if (final_type != NULL)
                break;

        }

    }

    else
    {
        if (basic == BTP_UCHAR || basic == BTP_USHORT || basic == BTP_UINT || basic == BTP_ULONG_LONG)
        {
            result = resolve_kaitai_expression_as_integer(locals,
                                                          kswitch->target,
                                                          strlen(kswitch->target),
                                                          &value);
            if (!result) goto exit_with_creator;

            for (i = 0; i < kswitch->count; i++)
            {
                final_type = is_suitable_switch_case_for_integer(kswitch->cases[i], locals, &value);

                if (final_type != NULL)
                    break;

            }

        }

        else
            printf("other type: %u\n", basic);

    }

    if (final_type == NULL && kswitch->defcase != NULL)
        final_type = kswitch->defcase->type;

    /* Mise en place d'un attribut et analyse */

    if (final_type != NULL)
    {
        attrib = g_kaitai_attribute_dup_for_user_type(kswitch->generic, final_type);

        result = g_kaitai_parser_parse_content(G_KAITAI_PARSER(attrib), locals, content, pos, record);

        g_object_unref(G_OBJECT(attrib));

    }

 exit_with_creator:

    g_object_unref(G_OBJECT(creator));

 exit_with_ref:

    g_object_unref(G_OBJECT(reference));

 exit:

    return result;

}
