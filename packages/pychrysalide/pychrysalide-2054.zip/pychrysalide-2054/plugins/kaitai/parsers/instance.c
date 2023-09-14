
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instance.c - spécification d'une instance Kaitai
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


#include "instance.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <plugins/yaml/pair.h>


#include "instance-int.h"
#include "../expression.h"
#include "../records/value.h"



/* -------------------- CORRESPONDANCE ENTRE INSTANCE ET BINAIRE -------------------- */


/* Initialise la classe des instances de spécification Kaitai. */
static void g_kaitai_instance_class_init(GKaitaiInstanceClass *);

/* Initialise une instance de spécification Kaitai. */
static void g_kaitai_instance_init(GKaitaiInstance *);

/* Supprime toutes les références externes. */
static void g_kaitai_instance_dispose(GKaitaiInstance *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_instance_finalize(GKaitaiInstance *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt un contenu binaire selon des spécifications Kaitai. */
static bool g_kaitai_instance_parse_content(GKaitaiInstance *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);



/* ---------------------------------------------------------------------------------- */
/*                      CORRESPONDANCE ENTRE INSTANCE ET BINAIRE                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une instance de la spécification Kaitai. */
G_DEFINE_TYPE(GKaitaiInstance, g_kaitai_instance, G_TYPE_KAITAI_ATTRIBUTE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instances de spécification Kaitai.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_instance_class_init(GKaitaiInstanceClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKaitaiParserClass *parser;             /* Ancêtre parent de la classe */
    GKaitaiAttributeClass *attrib;          /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_instance_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_instance_finalize;

    parser = G_KAITAI_PARSER_CLASS(klass);

    parser->parse = (parse_kaitai_fc)g_kaitai_instance_parse_content;

    attrib = G_KAITAI_ATTRIBUTE_CLASS(klass);

    attrib->get_label = (get_attribute_label_fc)g_kaitai_instance_get_name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de spécification Kaitai.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_instance_init(GKaitaiInstance *inst)
{
    inst->name = NULL;

    inst->io = NULL;
    inst->pos = NULL;
    inst->value = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_instance_dispose(GKaitaiInstance *inst)
{
    G_OBJECT_CLASS(g_kaitai_instance_parent_class)->dispose(G_OBJECT(inst));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_instance_finalize(GKaitaiInstance *inst)
{
    if (inst->name != NULL)
        free(inst->name);

    if (inst->io != NULL)
        free(inst->io);

    if (inst->pos != NULL)
        free(inst->pos);

    if (inst->value != NULL)
        free(inst->value);

    G_OBJECT_CLASS(g_kaitai_instance_parent_class)->finalize(G_OBJECT(inst));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = noeud Yaml contenant l'instance à constituer.       *
*                                                                             *
*  Description : Construit un lecteur d'instance Kaitai.                      *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiInstance *g_kaitai_instance_new(GYamlNode *parent)
{
    GKaitaiInstance *result;               /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_INSTANCE, NULL);

    if (!g_kaitai_instance_create(result, parent))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst   = lecteur d'instance Kaitai à initialiser pleinement. *
*                parent = noeud Yaml contenant l'instance à constituer.       *
*                                                                             *
*  Description : Met en place un lecteur d'instance Kaitai.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_instance_create(GKaitaiInstance *inst, GYamlNode *parent)
{
    bool result;                            /* Bilan à retourner           */
    const char *name;                       /* Désignation du type         */
    char *sub_path;                         /* Chemin d'accès suivant      */
    GYamlNode *sub;                         /* Contenu Yaml d'un type      */
    GYamlNode *node;                        /* Noeud particulier présent   */
    const char *value;                      /* Valeur Yaml particulière    */

    result = false;

    /* Extraction du nom */

    if (!G_IS_YAML_PAIR(parent))
        goto exit;

    name = g_yaml_pair_get_key(G_YAML_PAIR(parent));

    inst->name = strdup(name);

    /* Extraction des bases du type */

    asprintf(&sub_path, "/%s/", name);
    sub = g_yaml_node_find_first_by_path(parent, sub_path);
    free(sub_path);

    if (sub == NULL)
        goto exit;

    result = g_kaitai_attribute_create(G_KAITAI_ATTRIBUTE(inst), sub, false);

    /* Eventuel contenu imposé */

    node = g_yaml_node_find_first_by_path(sub, "/io");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));
        if (value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_loading;
        }

        inst->io = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Eventuelle positiion imposée */

    node = g_yaml_node_find_first_by_path(sub, "/pos");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        value = g_yaml_pair_get_value(G_YAML_PAIR(node));
        if (value == NULL)
        {
            g_object_unref(G_OBJECT(node));
            goto bad_loading;
        }

        inst->pos = strdup(value);

        g_object_unref(G_OBJECT(node));

    }

    /* Eventuelle formule de calcul d'une valeur */

    node = g_yaml_node_find_first_by_path(sub, "/value");

    if (node != NULL)
    {
        assert(G_IS_YAML_PAIR(node));

        inst->value = g_yaml_pair_aggregate_value(G_YAML_PAIR(node));

        g_object_unref(G_OBJECT(node));

        if (inst->value == NULL)
            goto bad_loading;

    }

 bad_loading:

    g_object_unref(G_OBJECT(sub));

 exit:

    if (result)
        result = (inst->pos != NULL || inst->value != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst = lecteur d'instance Kaitai à consulter.                *
*                                                                             *
*  Description : Indique le nom attribué à une instance Kaitai.               *
*                                                                             *
*  Retour      : Désignation pointant l'instance.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_instance_get_name(const GKaitaiInstance *inst)
{
    char *result;                           /* Valeur à renvoyer           */

    result = inst->name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inst   = lecteur d'instance Kaitai à consulter.              *
*                locals = variables locales pour les résolutions de types.    *
*                value  = valeur à sauvegarder sous une forme générique. [OUT]*
*                                                                             *
*  Description : Détermine la valeur d'un élément Kaitai entier calculé.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_instance_compute_value(const GKaitaiInstance *inst, const kaitai_scope_t *locals, resolved_value_t *value)
{
    bool result;                            /* Bilan à retourner           */

    if (inst->value == NULL)
        result = false;

    else
        result = resolve_kaitai_expression_as_any(locals,
                                                      inst->value,
                                                      strlen(inst->value),
                                                      value);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : inst    = structure Kaitai en cours de parcours.             *
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

static bool g_kaitai_instance_parse_content(GKaitaiInstance *inst, kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *work_area;                 /* Aire de travail             */
    GKaitaiStream *stream;                  /* Flux de données pour Kaitai */
    resolved_value_t offset;                /* Position à adopter          */
    vmpa2t forced_pos;                      /* Tete de lecture constituée  */
    GKaitaiParserClass *class;              /* Classe parente à solliciter */

    if (inst->value != NULL)
    {
        *record = G_MATCH_RECORD(g_record_value_new(inst, locals));

        result = (*record != NULL);

    }

    else
    {
        /* Contenu particulier */

        if (inst->io == NULL)
            work_area = content;

        else
        {
            result = resolve_kaitai_expression_as_stream(locals, inst->io, strlen(inst->io), &stream);
            if (!result) goto exit;

            work_area = g_kaitai_stream_get_content(stream);

            g_object_unref(G_OBJECT(stream));

        }

        /* Tête de lecture */

        g_binary_content_compute_start_pos(work_area, &forced_pos);

        result = resolve_kaitai_expression_as_integer(locals, inst->pos, strlen(inst->pos), &offset);
        if (!result) goto exit_with_content;

        if (offset.type == GVT_UNSIGNED_INTEGER)
            advance_vmpa(&forced_pos, offset.unsigned_integer);

        else
        {
            assert(offset.type == GVT_SIGNED_INTEGER);

            if (offset.signed_integer < 0)
            {
                result = false;
                goto exit_with_content;
            }

            advance_vmpa(&forced_pos, offset.signed_integer);

        }

        /* Lecture */

        class = G_KAITAI_PARSER_CLASS(g_kaitai_instance_parent_class);

        result = class->parse(G_KAITAI_PARSER(inst), locals, work_area, &forced_pos, record);

 exit_with_content:

        if (work_area != content)
            g_object_unref(G_OBJECT(work_area));

    }

 exit:

    return result;

}
