
/* Chrysalide - Outil d'analyse de fichiers binaires
 * attribute.c - spécification d'un attribut Kaitai
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


#include "attribute.h"


#include <assert.h>
#include <string.h>


#include <analysis/contents/restricted.h>
#include <plugins/yaml/pair.h>


#include "attribute-int.h"
#include "../expression.h"
#include "../scope.h"
#include "../records/empty.h"
#include "../records/item.h"
#include "../records/list.h"



/* -------------------- CORRESPONDANCE ENTRE ATTRIBUT ET BINAIRE -------------------- */


/* Initialise la classe des attributs de spécification Kaitai. */
static void g_kaitai_attribute_class_init(GKaitaiAttributeClass *);

/* Initialise un attribut de spécification Kaitai. */
static void g_kaitai_attribute_init(GKaitaiAttribute *);

/* Supprime toutes les références externes. */
static void g_kaitai_attribute_dispose(GKaitaiAttribute *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_attribute_finalize(GKaitaiAttribute *);

/* Traduit en type concret une chaîne de caractères. */
static bool g_kaitai_attribute_resolve_type(GKaitaiAttribute *, const char *);

/* Valide la cohérence des informations portées par l'attribut. */
static bool g_kaitai_attribute_check(const GKaitaiAttribute *);

/* Copie le coeur de la définition d'un lecteur d'attribut. */
static GKaitaiAttribute *g_kaitai_attribute_dup_for(const GKaitaiAttribute *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt un contenu binaire selon des spécifications Kaitai. */
static bool _g_kaitai_attribute_parse_content(GKaitaiAttribute *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);

/* Extrait d'un contenu une série d'octets avec terminaison. */
static bool g_kaitai_attribute_parse_terminated_bytes(GKaitaiAttribute *, const kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);

/* Détermine la zone de couverture finale d'une correspondance. */
static bool g_kaitai_attribute_compute_maybe_terminated_range(const GKaitaiAttribute *, const kaitai_scope_t *, const GBinContent *, const vmpa2t *, phys_t *, mrange_t *);

/* Parcourt un contenu binaire selon des spécifications Kaitai. */
static bool g_kaitai_attribute_parse_content(GKaitaiAttribute *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);



/* ---------------------------------------------------------------------------------- */
/*                      CORRESPONDANCE ENTRE ATTRIBUT ET BINAIRE                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un attribut de la spécification Kaitai. */
G_DEFINE_TYPE(GKaitaiAttribute, g_kaitai_attribute, G_TYPE_KAITAI_PARSER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des attributs de spécification Kaitai.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_attribute_class_init(GKaitaiAttributeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKaitaiParserClass *parser;             /* Version parente de la classe*/ 

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_attribute_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_attribute_finalize;

    parser = G_KAITAI_PARSER_CLASS(klass);

    parser->parse = (parse_kaitai_fc)g_kaitai_attribute_parse_content;

    klass->get_label = g_kaitai_attribute_get_raw_id;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un attribut de spécification Kaitai.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_attribute_init(GKaitaiAttribute *attrib)
{
    attrib->raw_id = NULL;
    attrib->orig_id = NULL;

    attrib->doc = NULL;

    attrib->payload = KAP_UNINITIALIZED;

    attrib->repetition = KAR_NO_REPETITION;
    attrib->repeat_controller = NULL;

    attrib->condition = NULL;

    init_szstr(&attrib->terminator);
    attrib->consume = true;
    attrib->include = false;
    attrib->eos_error = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_attribute_dispose(GKaitaiAttribute *attrib)
{
    if (attrib->payload & KAP_DYNAMIC_TYPE)
        g_clear_object(&attrib->switchon);

    G_OBJECT_CLASS(g_kaitai_attribute_parent_class)->dispose(G_OBJECT(attrib));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_attribute_finalize(GKaitaiAttribute *attrib)
{
    if (attrib->raw_id != NULL)
        free(attrib->raw_id);

    if (attrib->orig_id != NULL)
        free(attrib->orig_id);

    if (attrib->doc != NULL)
        free(attrib->doc);

    if (attrib->payload & KAP_FIXED_CONTENT)
        exit_szstr(&attrib->fixed_content);

    else if (attrib->payload & KAP_USER_TYPE)
        free(attrib->named_type);

    if (attrib->fixed_size != NULL)
        free(attrib->fixed_size);

    if (attrib->repeat_controller != NULL)
        free(attrib->repeat_controller);

    if (attrib->condition != NULL)
        free(attrib->condition);

    exit_szstr(&attrib->terminator);

    G_OBJECT_CLASS(g_kaitai_attribute_parent_class)->finalize(G_OBJECT(attrib));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Construit un lecteur d'attribut Kaitai.                      *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiAttribute *g_kaitai_attribute_new(GYamlNode *parent)
{
    GKaitaiAttribute *result;               /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_ATTRIBUTE, NULL);

    if (!g_kaitai_attribute_create(result, parent, true))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = lecteur d'attribut Kaitai à initialiser pleinement.*
*                parent  = noeud Yaml contenant l'attribut à constituer.      *
*                need_id = encadre la présence d'un champ "id".               *
*                                                                             *
*  Description : Met en place un lecteur d'attribut Kaitai.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_attribute_create(GKaitaiAttribute *attrib, GYamlNode *parent, bool need_id)
{
    bool result;                            /* Bilan à retourner           */
    GYamlNode *node;                        /* Noeud particulier présent   */
    const char *value;                      /* Valeur Yaml particulière    */
    char *rebuilt_value;                    /* Valeur Yaml rassemblée      */
    kaitai_scope_t fake;                    /* Contexte de circonstance    */
    resolved_value_t bytes;                 /* Données brutes obtenues     */
    GYamlNode *other_node;                  /* Autre noeud nécessaire      */

    result = false;

    /* Identifiant obligatoire */

    node = g_yaml_node_find_first_by_path(parent, "/id");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));
        if (value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_id;
        }

        attrib->raw_id = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    else if (need_id)
        goto bad_id;

    /* Identifiant facultatif */

    node = g_yaml_node_find_first_by_path(parent, "/-orig-id");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));
        if (value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_id;
        }

        attrib->orig_id = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Eventuelle documentation */

    node = g_yaml_node_find_first_by_path(parent, "/doc");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));
        if (value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_doc;
        }

        attrib->doc = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Champ contents */

    node = g_yaml_node_find_first_by_path(parent, "/contents");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        rebuilt_value = g_yaml_pair_aggregate_value(G_YAML_PAIR(node));

        if (rebuilt_value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_content;
        }

        fake.meta =  NULL;
        fake.root =  NULL;
        fake.parent =  NULL;
        fake.last =  NULL;

        if (!resolve_kaitai_expression_as_bytes(&fake, rebuilt_value, strlen(rebuilt_value), &bytes))
        {
            free(rebuilt_value);
            g_object_unref(G_OBJECT(node));
            goto bad_content;
        }

        free(rebuilt_value);

        attrib->fixed_content = bytes.bytes;

        g_object_unref(G_OBJECT(node));

        attrib->payload |= KAP_FIXED_CONTENT;

    }

    /* Charge portée par un type */

    node = g_yaml_node_find_first_by_path(parent, "/type");

    if (node != NULL)
    {
        if (attrib->payload & KAP_FIXED_CONTENT)
        {
            printf("Can not handle fixed content and type definition at the same time for an attribute.\n");
            goto bad_definition;
        }

        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
        {
            if (g_kaitai_attribute_resolve_type(attrib, value))
                attrib->payload |= KAP_BASIC_TYPE;

            else
            {
                attrib->named_type = strdup(value);
                attrib->payload |= KAP_USER_TYPE;
            }

        }

        else
        {
            attrib->switchon = g_kaitai_switch_new(parent, attrib);
            if (attrib->switchon == NULL) goto bad_definition;

            attrib->payload |= KAP_DYNAMIC_TYPE;

        }

        g_object_unref(G_OBJECT(node));

    }

    /* Répétitions contrôlées ? */

    node = g_yaml_node_find_first_by_path(parent, "/repeat");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
        {
            if (strcmp(value, "eos") == 0)
                attrib->repetition = KAR_END_OF_STREAM;

            else if (strcmp(value, "expr") == 0)
            {
                other_node = g_yaml_node_find_first_by_path(parent, "/repeat-expr");

                if (other_node != NULL)
                {
                    if (G_IS_YAML_PAIR(other_node))
                    {
                        value = g_yaml_pair_get_value(G_YAML_PAIR(other_node));

                        if (value != NULL)
                        {
                            attrib->repetition = KAR_EXPRESSION;
                            attrib->repeat_controller = strdup(value);
                        }
                        else
                            printf("Expected repeat expression\n");

                    }

                    g_object_unref(G_OBJECT(other_node));

                }

            }

            else if (strcmp(value, "until") == 0)
            {
                other_node = g_yaml_node_find_first_by_path(parent, "/repeat-until");

                if (other_node != NULL)
                {
                    assert(G_IS_YAML_PAIR(other_node));

                    value = g_yaml_pair_get_value(G_YAML_PAIR(other_node));

                    if (value != NULL)
                    {
                        attrib->repetition = KAR_UNTIL;
                        attrib->repeat_controller = strdup(value);
                    }
                    else
                        printf("Expected repeat expression\n");

                }

                g_object_unref(G_OBJECT(other_node));

            }

        }

        g_object_unref(G_OBJECT(node));

    }

    /* Intégration sous condition ? */

    node = g_yaml_node_find_first_by_path(parent, "/if");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
            attrib->condition = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Taille fixée ? */

    node = g_yaml_node_find_first_by_path(parent, "/size");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
        {
            attrib->fixed_size = strdup(value);
            attrib->payload |= KAP_SIZED;
        }

        g_object_unref(G_OBJECT(node));

        if ((attrib->payload & KAP_SIZED) == 0)
            goto bad_content;

    }

    /* Prise en considération d'une taille maximale */

    node = g_yaml_node_find_first_by_path(parent, "/size-eos");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL && strcmp(value, "true") == 0)
        {
            if (attrib->payload != KAP_UNINITIALIZED)
                /* printf warning */;

            attrib->payload |= KAP_SIZED_EOS;

        }

        g_object_unref(G_OBJECT(node));

    }

    /* Champ terminator */

    node = g_yaml_node_find_first_by_path(parent, "/terminator");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        rebuilt_value = g_yaml_pair_aggregate_value(G_YAML_PAIR(node));

        if (rebuilt_value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_content;
        }

        fake.meta =  NULL;
        fake.root =  NULL;
        fake.parent =  NULL;
        fake.last =  NULL;

        if (!resolve_kaitai_expression_as_bytes(&fake, rebuilt_value, strlen(rebuilt_value), &bytes))
        {
            free(rebuilt_value);
            g_object_unref(G_OBJECT(node));
            goto bad_content;
        }

        free(rebuilt_value);

        if (attrib->terminator.data != NULL)
            printf("A ending content has already been specified (implicitly by the strz type)");

        else
        {
            attrib->terminator.data = bytes.bytes.data;
            attrib->terminator.len = bytes.bytes.len;
        }

        g_object_unref(G_OBJECT(node));

    }

    /* Champ consume */

    node = g_yaml_node_find_first_by_path(parent, "/consume");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
        {
            if (strcmp(value, "true") == 0)
                attrib->consume = true;

            else if (strcmp(value, "false") == 0)
                attrib->consume = false;

            else
                printf("Unsupported value for the 'consume' property (expecting true of false)");

        }

        g_object_unref(G_OBJECT(node));

    }

    /* Champ include */

    node = g_yaml_node_find_first_by_path(parent, "/include");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
        {
            if (strcmp(value, "true") == 0)
                attrib->include = true;

            else if (strcmp(value, "false") == 0)
                attrib->include = false;

            else
                printf("Unsupported value for the 'include' property (expecting true of false)");

        }

        g_object_unref(G_OBJECT(node));

    }

    /* Champ eos-error */

    node = g_yaml_node_find_first_by_path(parent, "/eos-error");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));

        if (value != NULL)
        {
            if (strcmp(value, "true") == 0)
                attrib->eos_error = true;

            if (strcmp(value, "false") == 0)
                attrib->eos_error = false;

            else
                printf("Unsupported value for the 'eos_error' property (expecting true of false)");

        }

        g_object_unref(G_OBJECT(node));

    }

    /* Validation finale */

    result = g_kaitai_attribute_check(attrib);

 bad_definition:

 bad_doc:
 bad_id:
 bad_content:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = attribut Kaitai en cours de constitution.           *
*                desc   = chaîne de caractère à interpréter en type.          *
*                                                                             *
*  Description : Traduit en type concret une chaîne de caractères.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_kaitai_attribute_resolve_type(GKaitaiAttribute *attrib, const char *desc)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    attrib->basic = BTP_INVALID;
    attrib->has_endian = false;

    /**
     * Cf. définition des types de base existants :
     * http://doc.kaitai.io/user_guide.html#_fixed_size_structures
     */

#define RESOLVE_ENDIAN                      \
    if (desc[2] == 'l')                     \
    {                                       \
        if (desc[3] == 'e')                 \
        {                                   \
            attrib->endian = SRE_LITTLE;    \
            attrib->has_endian = true;      \
        }                                   \
    }                                       \
    else if (desc[2] == 'b')                \
    {                                       \
        if (desc[3] == 'e')                 \
        {                                   \
            attrib->endian = SRE_BIG;       \
            attrib->has_endian = true;      \
        }                                   \
    }                                       \

    /* Analyse de la chaîne fournie */

    switch (desc[0])
    {
        case 'f':
            switch (desc[1])
            {
                case '4':
                    attrib->basic = BTP_754R_32;
                    RESOLVE_ENDIAN;
                    break;

                case '8':
                    attrib->basic = BTP_754R_64;
                    RESOLVE_ENDIAN;
                    break;

                default:
                    result = false;
                    break;

            }
            break;

        case 's':
            switch (desc[1])
            {
                case '1':
                    attrib->basic = BTP_CHAR;
                    RESOLVE_ENDIAN;
                    break;

                case '2':
                    attrib->basic = BTP_SHORT;
                    RESOLVE_ENDIAN;
                    break;

                case '4':
                    attrib->basic = BTP_INT;
                    RESOLVE_ENDIAN;
                    break;

                case '8':
                    attrib->basic = BTP_LONG_LONG;
                    RESOLVE_ENDIAN;
                    break;

                case 't':
                    if (desc[2] == 'r')
                    {
                        attrib->basic = BTP_CHAR;
                        attrib->is_string = true;
                        if (desc[3] == 'z')
                        {
                            attrib->terminator.data = strdup("");
                            attrib->terminator.len = 1;
                        }
                    }
                    else
                        result = false;
                    break;

                default:
                    result = false;
                    break;

            }
            break;

        case 'u':
            switch (desc[1])
            {
                case '1':
                    attrib->basic = BTP_UCHAR;
                    RESOLVE_ENDIAN;
                    break;

                case '2':
                    attrib->basic = BTP_USHORT;
                    RESOLVE_ENDIAN;
                    break;

                case '4':
                    attrib->basic = BTP_UINT;
                    RESOLVE_ENDIAN;
                    break;

                case '8':
                    attrib->basic = BTP_ULONG_LONG;
                    RESOLVE_ENDIAN;
                    break;

                default:
                    result = false;
                    break;

            }
            break;

        default:
            result = false;
            break;

    }

    /* Vérification d'une comparaison complète */
    if (result)
        switch (attrib->basic)
        {
            case BTP_CHAR:
                if (attrib->is_string)
                {
                    if (attrib->terminator.data != NULL)
                        result = (desc[4] == 0);
                    else
                        result = (desc[3] == 0);
                }
                else
                {
                    if (attrib->has_endian)
                        result = (desc[4] == 0);
                    else
                        result = (desc[2] == 0);
                }
                break;

            default:
                if (attrib->has_endian)
                    result = (desc[4] == 0);
                else
                    result = (desc[2] == 0);
                break;

        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = attribut Kaitai à valider.                          *
*                                                                             *
*  Description : Valide la cohérence des informations portées par l'attribut. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_kaitai_attribute_check(const GKaitaiAttribute *attrib)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    /**
     * Une lecture de tous les octets restants ne doit correspondre qu'à des octets bruts.
     */
    if (attrib->payload & KAP_SIZED_EOS && attrib->payload != KAP_SIZED_EOS)
    {
        result = (attrib->payload & KAP_BASIC_TYPE) && attrib->is_string;

        if (!result)
        {
            printf("Reading all the remaining bytes should only produce bytes.");
            result = true;
        }

    }

    /**
     * Une chaîne (type str[z]) doit comporter une séquence de terminaison.
     */
    if ((attrib->payload & KAP_BASIC_TYPE) && attrib->is_string)
    {
        result = (attrib->terminator.data != NULL) || (attrib->payload & (KAP_SIZED | KAP_SIZED_EOS));

        if (!result)
        {
            printf("An unsized string (str type with no size attribute) has to be link to a terminator sequence.");
            goto exit;
        }

    }

    /**
     * Si une séquence d'octets finaux est spécifiées, alors l'attribut
     * doit correspondre à un type str[z] (lecture) ou de taille fixée
     * (validation post-lecture).
     */
    if (attrib->terminator.data != NULL)
    {
        result = ((attrib->payload & ~(KAP_FIXED_CONTENT | KAP_BASIC_TYPE | KAP_SIZED)) == 0);

        if (result && (attrib->payload & KAP_BASIC_TYPE))
            result = attrib->is_string;

        if (!result)
        {
            printf("A useless terminator is specified.");
            result = true;
            goto exit;
        }

    }

    /**
     * Il n'est pas possible d'inclure un marqueur de fin sans le consommer.
     */
    if (!attrib->consume && attrib->include)
    {
        result = false;
        printf("It is not possible to include a terminator without consuming it.");
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à dupliquer.              *
*                type   = type utilisateur à associer au nouvel attribut.     *
*                                                                             *
*  Description : Dérive un lecteur d'attribut Kaitai pour un type utilisateur.*
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiAttribute *g_kaitai_attribute_dup_for_user_type(const GKaitaiAttribute *attrib, const char *type)
{
    GKaitaiAttribute *result;               /* Structure à retourner       */

    result = g_kaitai_attribute_dup_for(attrib);

    result->payload = KAP_USER_TYPE;

    result->named_type = strdup(type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à dupliquer.              *
*                                                                             *
*  Description : Copie le coeur de la définition d'un lecteur d'attribut.     *
*                                                                             *
*  Retour      : Nouvelle instance à compléter.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GKaitaiAttribute *g_kaitai_attribute_dup_for(const GKaitaiAttribute *attrib)
{
    GKaitaiAttribute *result;               /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_ATTRIBUTE, NULL);

    /**
     * Il n'y a rien à copier dans la structure parente.
     *
     * Les travaux de copie ne portent ainsi que sur le présent attribut.
     */

    result->raw_id = strdup(attrib->raw_id);

    if (attrib->orig_id != NULL)
        result->orig_id = strdup(attrib->orig_id);

    if (attrib->doc != NULL)
        result->doc = strdup(attrib->doc);

    if (attrib->fixed_size != NULL)
        result->fixed_size = strdup(attrib->fixed_size);

    result->repetition = attrib->repetition;

    if (attrib->repeat_controller != NULL)
        result->repeat_controller = strdup(attrib->repeat_controller);

    if (attrib->condition != NULL)
        result->condition = strdup(attrib->condition);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à consulter.              *
*                                                                             *
*  Description : Indique l'étiquette à utiliser pour identifier un attribut.  *
*                                                                             *
*  Retour      : Valeur brute de l'identifiant.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_attribute_get_label(const GKaitaiAttribute *attrib)
{
    const char *result;                     /* Valeur à renvoyer           */
    GKaitaiAttributeClass *class;           /* Classe de l'instance        */

    class = G_KAITAI_ATTRIBUTE_GET_CLASS(attrib);

    result = class->get_label(attrib);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à consulter.              *
*                                                                             *
*  Description : Indique la désignation brute d'un identifiant Kaitai.        *
*                                                                             *
*  Retour      : Valeur brute de l'identifiant.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_attribute_get_raw_id(const GKaitaiAttribute *attrib)
{
    char *result;                           /* Valeur à renvoyer           */

    result = attrib->raw_id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à consulter.              *
*                                                                             *
*  Description : Indique la désignation originelle d'un identifiant Kaitai.   *
*                                                                             *
*  Retour      : Valeur originelle de l'identifiant.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_attribute_get_original_id(const GKaitaiAttribute *attrib)
{
    char *result;                           /* Valeur à renvoyer           */

    result = attrib->orig_id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à consulter.              *
*                                                                             *
*  Description : Fournit une éventuelle documentation concernant l'attribut.  *
*                                                                             *
*  Retour      : Description enregistrée ou NULL si absente.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_attribute_get_doc(const GKaitaiAttribute *attrib)
{
    char *result;                           /* Valeur à renvoyer           */

    result = attrib->doc;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à consulter.              *
*                                                                             *
*  Description : Indique la nature de la charge représentée par l'attribut.   *
*                                                                             *
*  Retour      : Forme de contenu représenté par le lecteur d'attribut.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

KaitaiAttributePayload g_kaitai_attribute_get_payload(const GKaitaiAttribute *attrib)
{
    KaitaiAttributePayload result;          /* Type de charge à renvoyer   */

    result = attrib->payload;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib    = lecteur d'attribut Kaitai à consulter.           *
*                basic     = type de base Kaitai reconnu par le lecteur. [OUT]*
*                is_string = nature du type BTP_CHAR en sortie. [OUT]         *
*                                                                             *
*  Description : Précise un éventuel type de base reconnu par le lecteur.     *
*                                                                             *
*  Retour      : Validité du type renseigné en argument.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_attribute_get_basic_type(const GKaitaiAttribute *attrib, BaseType *basic, bool *is_string)
{
    bool result;                            /* Validité à retourner        */

    result = (attrib->payload & KAP_BASIC_TYPE);

    if (result)
    {        
        *basic = attrib->basic;
        *is_string = attrib->is_string;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = lecteur d'attribut Kaitai à consulter.             *
*                content = contenu binaire à venir lire.                      *
*                range   = espace disponible pour la lecture.                 *
*                out     = tableau d'octets retournés. [OUT]                  *
*                len     = taille de ce tableau alloué. [OUT]                 *
*                                                                             *
*  Description : Lit les octets d'une chaîne représentée.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_attribute_read_truncated_bytes(const GKaitaiAttribute *attrib, const GBinContent *content, const mrange_t *range, bin_t **out, size_t *len)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t tmppos;                          /* Localisation modifiable     */
    const bin_t *data;                      /* Accès aux données brutes    */

    result = false;

    if ((attrib->payload & KAP_SIZED) == 0)
        goto bad_type;

    copy_vmpa(&tmppos, get_mrange_addr(range));

    *len = get_mrange_length(range);

    data = g_binary_content_get_raw_access(content, &tmppos, *len);

    *out = malloc(sizeof(bin_t) * (*len + 1));

    memcpy(*out, data, *len);
    (*out)[*len] = '\0';

    result = true;

 bad_type:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib = lecteur d'attribut Kaitai à consulter.              *
*                                                                             *
*  Description : Détermine si l'attribue porte une valeur entière signée.     *
*                                                                             *
*  Retour      : Bilan de la consultation : true si un entier signé est visé. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_attribute_handle_signed_integer(const GKaitaiAttribute *attrib)
{
    bool result;                            /* Bilan à retourner           */

    result = false;

    if ((attrib->payload & KAP_BASIC_TYPE) == 0)
        goto bad_type;

    switch (attrib->basic)
    {
        case BTP_CHAR:
        case BTP_SHORT:
        case BTP_INT:
        case BTP_LONG_LONG:
            result = true;
            break;

        default:
            break;

    }

 bad_type:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = lecteur d'attribut Kaitai à consulter.             *
*                content = contenu binaire à venir lire.                      *
*                range   = espace de lecture.                                 *
*                endian  = boustime des données à respecter.                  *
*                out     = valeur à sauvegarder sous une forme générique.[OUT]*
*                                                                             *
*  Description : Lit la valeur d'un élément Kaitai entier représenté.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_attribute_read_value(const GKaitaiAttribute *attrib, const GBinContent *content, const mrange_t *range, SourceEndian endian, resolved_value_t *out)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t tmppos;                          /* Localisation modifiable     */
    const bin_t *data;                      /* Données brutes restituées   */
    int8_t stmp8;                           /* Valeur de 8 bits lue        */
    uint8_t tmp8;                           /* Valeur de 8 bits lue        */
    int16_t stmp16;                         /* Valeur de 16 bits lue       */
    uint16_t tmp16;                         /* Valeur de 16 bits lue       */
    int32_t stmp32;                         /* Valeur de 32 bits lue       */
    uint32_t tmp32;                         /* Valeur de 32 bits lue       */
    int64_t stmp64;                         /* Valeur de 64 bits lue       */
    uint64_t tmp64;                         /* Valeur de 64 bits lue       */

    result = false;

    if (attrib->payload & (KAP_FIXED_CONTENT | KAP_SIZED | KAP_SIZED_EOS))
    {
        copy_vmpa(&tmppos, get_mrange_addr(range));

        data = g_binary_content_get_raw_access(content, &tmppos, get_mrange_length(range));
        result = (data != NULL);

        if (result)
        {
            out->type = GVT_BYTES;

            out->bytes.len = get_mrange_length(range);

            out->bytes.data = malloc(out->bytes.len);
            memcpy(out->bytes.data, data, out->bytes.len);

        }

    }

    else if (attrib->payload & KAP_BASIC_TYPE)
    {
        copy_vmpa(&tmppos, get_mrange_addr(range));

        switch (attrib->basic)
        {
            case BTP_CHAR:
                if (attrib->is_string)
                {
                    copy_vmpa(&tmppos, get_mrange_addr(range));

                    data = g_binary_content_get_raw_access(content, &tmppos, get_mrange_length(range));
                    result = (data != NULL);

                    if (result)
                    {
                        out->type = GVT_BYTES;

                        out->bytes.len = get_mrange_length(range);

                        out->bytes.data = malloc(out->bytes.len);
                        memcpy(out->bytes.data, data, out->bytes.len);

                    }

                }
                else
                {
                    assert(get_mrange_length(range) == 1);
                    result = g_binary_content_read_s8(content, &tmppos, &stmp8);
                    out->type = GVT_SIGNED_INTEGER;
                    out->signed_integer = stmp8;
                }
                break;

            case BTP_UCHAR:
                assert(get_mrange_length(range) == 1);
                result = g_binary_content_read_u8(content, &tmppos, &tmp8);
                out->type = GVT_UNSIGNED_INTEGER;
                out->unsigned_integer = tmp8;
                break;

            case BTP_SHORT:
                assert(get_mrange_length(range) == 2);
                result = g_binary_content_read_s16(content, &tmppos, endian, &stmp16);
                out->type = GVT_SIGNED_INTEGER;
                out->signed_integer = stmp16;
                break;

            case BTP_USHORT:
                assert(get_mrange_length(range) == 2);
                result = g_binary_content_read_u16(content, &tmppos, endian, &tmp16);
                out->type = GVT_UNSIGNED_INTEGER;
                out->unsigned_integer = tmp16;
                break;

            case BTP_INT:
                assert(get_mrange_length(range) == 4);
                result = g_binary_content_read_s32(content, &tmppos, endian, &stmp32);
                out->type = GVT_SIGNED_INTEGER;
                out->signed_integer = stmp32;
                break;

            case BTP_UINT:
                assert(get_mrange_length(range) == 4);
                result = g_binary_content_read_u32(content, &tmppos, endian, &tmp32);
                out->type = GVT_UNSIGNED_INTEGER;
                out->unsigned_integer = tmp32;
                break;

            case BTP_LONG_LONG:
                assert(get_mrange_length(range) == 8);
                result = g_binary_content_read_s64(content, &tmppos, endian, &stmp64);
                out->type = GVT_SIGNED_INTEGER;
                out->signed_integer = stmp64;
                break;

            case BTP_ULONG_LONG:
                assert(get_mrange_length(range) == 8);
                result = g_binary_content_read_u64(content, &tmppos, endian, &tmp64);
                out->type = GVT_UNSIGNED_INTEGER;
                out->unsigned_integer = tmp64;
                break;

            default:
                break;

        }

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = structure Kaitai en cours de parcours.             *
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

static bool _g_kaitai_attribute_parse_content(GKaitaiAttribute *attrib, kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    resolved_value_t authorized;            /* Validation des traitements  */

    mrange_t work_range;                    /* Définition de cette aire    */
    GBinContent *work_area;                 /* Aire de travail             */
    bool has_empty_size;                    /* Mémorise une taille nulle   */


    //unsigned long long value;               /* Valeur entière finale       */
    //bool status;                            /* Bilan d'une conversion      */


    vmpa2t tmp;                             /* Position de travail         */
    phys_t diff;                            /* Différentiel de positions   */
    resolved_value_t resolved;              /* Valeur entière obtenue      */
    phys_t max_size;                        /* Taille maximale imposée     */


    const bin_t *data;                      /* Données à comparer          */
    GKaitaiType *user_type;                 /* Définition particulière     */


    mrange_t range;                         /* Couverture appliquée        */
    SourceEndian endian;                    /* Boutisme à observer         */
    phys_t cur_diff;                        /* Avancée de lecture courante */


    result = false;
    *record = NULL;

    /* Lecture soumise à condition ? */

    if (attrib->condition != NULL)
    {
        result = resolve_kaitai_expression_as_boolean(locals,
                                                      attrib->condition,
                                                      strlen(attrib->condition),
                                                      &authorized);

        if (!result || !authorized.status)
            goto exit;

    }

    /* Zone de travail restreinte */

    g_binary_content_compute_end_pos(content, &tmp);
    diff = compute_vmpa_diff(pos, &tmp);

    if (attrib->payload & KAP_SIZED)
    {
        result = resolve_kaitai_expression_as_integer(locals,
                                                      attrib->fixed_size,
                                                      strlen(attrib->fixed_size),
                                                      &resolved);

        if (result)
        {
            if (resolved.type == GVT_UNSIGNED_INTEGER)
                max_size = resolved.unsigned_integer;
            else
            {
                assert(resolved.type == GVT_SIGNED_INTEGER);

                if (resolved.signed_integer < 0)
                    result = false;
                else
                    max_size = resolved.signed_integer;

            }

            if (result)
                result = (diff >= max_size);

            if (!result)
                printf("Need more data!\n");

            if (result && max_size < diff)
                diff = max_size;

        }

        if (!result)
            goto exit;

        init_mrange(&work_range, pos, diff);
        work_area = g_restricted_content_new_ro(content, &work_range);

        has_empty_size = (diff == 0);

    }
    else
    {
        work_area = content;
        has_empty_size = false;
    }

    /* Etablissement d'une zone de correspondance */

    if (attrib->payload == KAP_UNINITIALIZED)
        assert(false);

    else if (attrib->payload & KAP_SIZED_EOS)
        result = true;

    else if (attrib->payload & KAP_FIXED_CONTENT)
    {
        if (diff >= attrib->fixed_content.len)
        {
            copy_vmpa(&tmp, pos);

            data = g_binary_content_get_raw_access(work_area, &tmp, attrib->fixed_content.len);
            assert(data != NULL);

            result = (memcmp(data, attrib->fixed_content.data, attrib->fixed_content.len) == 0);

            if (result)
                diff = attrib->fixed_content.len;

        }

    }

    else if (attrib->payload & KAP_BASIC_TYPE)
    {
        switch (attrib->basic)
        {
            case BTP_CHAR:
            case BTP_UCHAR:
                if (attrib->is_string)
                {
                    if ((attrib->payload & KAP_SIZED) == 0)
                        result = g_kaitai_attribute_parse_terminated_bytes(attrib, locals, work_area, pos, record);
                }
                else
                {
                    result = (diff >= 1);
                    diff = 1;
                }
                break;

            case BTP_SHORT:
            case BTP_USHORT:
                result = (diff >= 2);
                diff = 2;
                break;

            case BTP_INT:
            case BTP_UINT:
            case BTP_754R_32:
                result = (diff >= 4);
                diff = 4;
                break;

            case BTP_LONG_LONG:
            case BTP_ULONG_LONG:
            case BTP_754R_64:
                result = (diff >= 8);
                diff = 8;
                break;

            default:
                break;

        }

    }

    else if (attrib->payload & KAP_USER_TYPE)
    {
        user_type = find_sub_type(locals, attrib->named_type);

        if (user_type != NULL)
        {
            result = g_kaitai_parser_parse_content(G_KAITAI_PARSER(user_type),
                                                   locals, work_area, pos, record);       

            if (result)
                /**
                 * Le type utilisateur dérive du type GKaitaiStruct, qui ne possède pas
                 * d'identifiant propre. La correspondance produite est ainsi nominalement
                 * anonyme, ce qui empêche toute résolution.
                 *
                 * Le rattachement de l'étiquette de l'attribut d'origine est donc forcée ici.
                 */
                g_match_record_fix_creator(*record, G_KAITAI_PARSER(attrib));


            g_object_unref(G_OBJECT(user_type));

        }

    }

    else if (attrib->payload & KAP_DYNAMIC_TYPE)
        result = g_kaitai_parser_parse_content(G_KAITAI_PARSER(attrib->switchon), locals, work_area, pos, record);

    else if (attrib->payload & KAP_SIZED)
    {
        /* Cas déjà traité en début de fonction */

    }

    /* Enregistrement de la correspondance */

    if (result && *record == NULL)
    {
        /**
         * On choisit de laisser la création de correspondances nulles.
         *
         * Cela permet de disposer de la présence de champs valides, même vides
         * (cf. "4.10.3. Repeat until condition is met")
         */

        /* if (diff > 0) */
        {
            result = g_kaitai_attribute_compute_maybe_terminated_range(attrib, locals, content, pos, &diff, &range);

            if (result)
            {
                if (has_empty_size)
                    *record = G_MATCH_RECORD(g_record_empty_new(G_KAITAI_PARSER(attrib), content, pos));

                else
                {
                    if (attrib->has_endian)
                        endian = attrib->endian;
                    else
                        endian = g_kaitai_meta_get_endian(locals->meta);

                    *record = G_MATCH_RECORD(g_record_item_new(attrib, work_area, &range, endian));

                    if (*record != NULL)
                        advance_vmpa(pos, diff);
                    else
                        result = false;

                }

            }

        }

    }

    /* Libération de zone de travail restreinte ? */

    if (attrib->payload & KAP_SIZED)
    {
        cur_diff = compute_vmpa_diff(get_mrange_addr(&work_range), pos);

        /* Pour GCC... */
        max_size = get_mrange_length(&work_range);

        if (cur_diff < max_size)
            advance_vmpa(pos, max_size - cur_diff);

        assert(work_area != content);
        g_object_unref(G_OBJECT(work_area));

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = structure Kaitai en cours de parcours.             *
*                locals  = variables locales pour les résolutions de types.   *
*                content = données binaires à analyser et traduire.           *
*                pos     = tête de lecture courante. [OUT]                    *
*                record  = noeud d'arborescence d'éléments rencontrés. [OUT]  *
*                                                                             *
*  Description : Extrait d'un contenu une série d'octets avec terminaison.    *
*                                                                             *
*  Retour      : Bilan de l'opératon : true pour continuer, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_kaitai_attribute_parse_terminated_bytes(GKaitaiAttribute *attrib, const kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    sized_string_t marker;                  /* Marqueur potentiel à tester */
    vmpa2t iter;                            /* Tête de lecture courante    */
    vmpa2t end;                             /* Fin du parcours possible    */
    vmpa2t tmp;                             /* Position à mouvante         */
    phys_t diff;                            /* Avancée de lecture courante */
    mrange_t range;                         /* Couverture appliquée        */
    SourceEndian endian;                    /* Boutisme à observer         */

    result = false;

    /* Recherche du marqueur de fin */

    marker.len = attrib->terminator.len;

    copy_vmpa(&iter, pos);
    g_binary_content_compute_end_pos(content, &end);

    while (cmp_vmpa_by_phy(&iter, &end) < 0)
    {
        copy_vmpa(&tmp, &iter);

        marker.data = (char *)g_binary_content_get_raw_access(content, &tmp, marker.len);
        if (marker.data == NULL) break;

        if (szmemcmp(&marker, &attrib->terminator) == 0)
        {
            result = true;
            break;
        }

        advance_vmpa(&iter, 1);

    }

    /* Si la recherche a abouti */

    if (result)
    {
        diff = compute_vmpa_diff(pos, &iter);

        if (attrib->include)
            diff += marker.len;

        init_mrange(&range, pos, diff);

        if (attrib->has_endian)
            endian = attrib->endian;
        else
            endian = g_kaitai_meta_get_endian(locals->meta);

        *record = G_MATCH_RECORD(g_record_item_new(attrib, content, &range, endian));

        copy_vmpa(pos, &iter);

        if (attrib->consume)
            advance_vmpa(pos, marker.len);

    }

    /* Sinon l'absence de marqueur est-elle tolérée ? */

    else if (!attrib->eos_error)
    {
        diff = compute_vmpa_diff(pos, &end);

        init_mrange(&range, pos, diff);

        if (attrib->has_endian)
            endian = attrib->endian;
        else
            endian = g_kaitai_meta_get_endian(locals->meta);

        *record = G_MATCH_RECORD(g_record_item_new(attrib, content, &range, endian));

        copy_vmpa(pos, &end);

        result = true;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = structure Kaitai en cours de parcours.             *
*                locals  = variables locales pour les résolutions de types.   *
*                content = données binaires à analyser et traduire.           *
*                pos     = tête de lecture courante.                          *
*                maxsize = taille maximale de la zone de correspondance. [OUT]*
*                range   = zone de couverture à officialiser. [OUT]           *
*                                                                             *
*  Description : Détermine la zone de couverture finale d'une correspondance. *
*                                                                             *
*  Retour      : Bilan de l'opératon : true pour continuer, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_kaitai_attribute_compute_maybe_terminated_range(const GKaitaiAttribute *attrib, const kaitai_scope_t *locals, const GBinContent *content, const vmpa2t *pos, phys_t *maxsize, mrange_t *range)
{
    bool result;                            /* Bilan à retourner           */
    sized_string_t marker;                  /* Marqueur potentiel à tester */
    vmpa2t iter;                            /* Tête de lecture courante    */
    vmpa2t end;                             /* Fin du parcours possible    */
    vmpa2t tmp;                             /* Position à mouvante         */
    phys_t diff;                            /* Avancée de lecture courante */

    if (attrib->terminator.data == NULL)
    {
        init_mrange(range, pos, *maxsize);
        result = true;
    }

    else
    {
        result = false;

        if (attrib->terminator.len > *maxsize)
            goto exit;

        /* Recherche du marqueur de fin */

        marker.len = attrib->terminator.len;

        copy_vmpa(&iter, pos);

        copy_vmpa(&tmp, pos);
        advance_vmpa(&tmp, *maxsize - marker.len);

        while (cmp_vmpa_by_phy(&iter, &end) <= 0)
        {
            copy_vmpa(&tmp, &iter);

            marker.data = (char *)g_binary_content_get_raw_access(content, &tmp, marker.len);
            if (marker.data == NULL) break;

            if (szmemcmp(&marker, &attrib->terminator) == 0)
            {
                result = true;
                break;
            }

            advance_vmpa(&iter, 1);

        }

        /* Si la recherche a abouti */

        if (result)
        {
            diff = compute_vmpa_diff(pos, &iter);

            if (attrib->include)
                init_mrange(range, pos, diff + marker.len);
            else
                init_mrange(range, pos, diff);

            assert((diff + marker.len) <= *maxsize);

            if (attrib->consume)
                *maxsize = diff + marker.len;
            else
                *maxsize = diff;

        }

        /* Sinon l'absence de marqueur est-elle tolérée ? */

        else if (!attrib->eos_error)
        {
            init_mrange(range, pos, *maxsize);
            result = true;
        }

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : attrib  = structure Kaitai en cours de parcours.             *
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

static bool g_kaitai_attribute_parse_content(GKaitaiAttribute *attrib, kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    resolved_value_t authorized;            /* Validation des traitements  */
    GRecordList *list;                      /* Constitution d'une liste    */
    vmpa2t end;                             /* Position maximale du flux   */
    phys_t diff;                            /* Différentiel de positions   */
    GMatchRecord *child;                    /* Element de liste à intégrer */
    resolved_value_t resolved;              /* Valeur entière obtenue      */
    unsigned long long count;               /* Nombre d'itérations à mener */
    unsigned long long i;                   /* Boucle de parcours          */
    resolved_value_t loop;                  /* Poursuite des lectures ?    */

    if (attrib->repetition == KAR_NO_REPETITION)
        result = _g_kaitai_attribute_parse_content(attrib, locals, content, pos, record);

    else
    {
        /* Lecture soumise à condition ? */

        if (attrib->condition != NULL)
        {
            result = resolve_kaitai_expression_as_boolean(locals,
                                                          attrib->condition,
                                                          strlen(attrib->condition),
                                                          &authorized);

            if (!result || !authorized.status)
                goto exit;

        }

        list = g_record_list_new(attrib, content, pos);

        switch (attrib->repetition)
        {
            case KAR_END_OF_STREAM:

                result = true;

                g_binary_content_compute_end_pos(content, &end);
                diff = compute_vmpa_diff(pos, &end);

                while (diff > 0)
                {
                    result = _g_kaitai_attribute_parse_content(attrib, locals, content, pos, &child);
                    if (!result) break;

                    g_record_list_add_record(list, child);
                    remember_last_record(locals, child);

                    diff = compute_vmpa_diff(pos, &end);

                }

                break;

            case KAR_EXPRESSION:

                result = resolve_kaitai_expression_as_integer(locals,
                                                              attrib->repeat_controller,
                                                              strlen(attrib->repeat_controller),
                                                              &resolved);

                if (resolved.type == GVT_UNSIGNED_INTEGER)
                    count = resolved.unsigned_integer;
                else
                {
                    assert(resolved.type == GVT_SIGNED_INTEGER);

                    if (resolved.signed_integer < 0)
                    {
                        result = false;
                        break;
                    }

                    count = resolved.signed_integer;

                }

                for (i = 0; i < count; i++)
                {
                    result = _g_kaitai_attribute_parse_content(attrib, locals, content, pos, &child);
                    if (!result) break;

                    g_record_list_add_record(list, child);
                    remember_last_record(locals, child);

                }

                break;

            case KAR_UNTIL:

                do
                {
                    result = _g_kaitai_attribute_parse_content(attrib, locals, content, pos, &child);
                    if (!result) break;

                    g_record_list_add_record(list, child);
                    remember_last_record(locals, child);

                    result = resolve_kaitai_expression_as_boolean(locals,
                                                                  attrib->repeat_controller,
                                                                  strlen(attrib->repeat_controller),
                                                                  &loop);
                    if (!result) break;

                }
                while (!loop.status);

                break;

            default:
                break;

        }

        if (!result) g_clear_object(&list);

        *record = G_MATCH_RECORD(list);

    }

 exit:

    return result;

}
