
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


#include "struct.h"


#include <assert.h>
#include <string.h>


#include <plugins/yaml/collection.h>
#include <plugins/yaml/parser.h>


#include "struct-int.h"
#include "../parser.h"
#include "../records/empty.h"
#include "../records/group.h"



/* ---------------------- LECTURE D'UNE TRANCHE DE DEFINITIONS ---------------------- */


/* Initialise la classe des structuts de spécification Kaitai. */
static void g_kaitai_structure_class_init(GKaitaiStructClass *);

/* Initialise un structut de spécification Kaitai. */
static void g_kaitai_structure_init(GKaitaiStruct *);

/* Supprime toutes les références externes. */
static void g_kaitai_structure_dispose(GKaitaiStruct *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_structure_finalize(GKaitaiStruct *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt un contenu binaire selon des spécifications Kaitai. */
static bool g_kaitai_structure_parse_content(GKaitaiStruct *, kaitai_scope_t *, GBinContent *, vmpa2t *, GMatchRecord **);



/* ---------------------------------------------------------------------------------- */
/*                        LECTURE D'UNE TRANCHE DE DEFINITIONS                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un structut de la spécification Kaitai. */
G_DEFINE_TYPE(GKaitaiStruct, g_kaitai_structure, G_TYPE_KAITAI_PARSER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des structuts de spécification Kaitai.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_structure_class_init(GKaitaiStructClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GKaitaiParserClass *parser;             /* Version parente de la classe*/ 

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_structure_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_structure_finalize;

    parser = G_KAITAI_PARSER_CLASS(klass);

    parser->parse = (parse_kaitai_fc)g_kaitai_structure_parse_content;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise un structure de spécification Kaitai.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_structure_init(GKaitaiStruct *kstruct)
{
    kstruct->meta = NULL;

    kstruct->seq_items = NULL;
    kstruct->seq_items_count = 0;

    kstruct->types = NULL;
    kstruct->types_count = 0;

    kstruct->instances = NULL;
    kstruct->instances_count = 0;

    kstruct->enums = NULL;
    kstruct->enums_count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_structure_dispose(GKaitaiStruct *kstruct)
{
    size_t i;                               /* Boucle de parcours          */

    g_clear_object(&kstruct->meta);

    for (i = 0; i < kstruct->seq_items_count; i++)
        g_clear_object(&kstruct->seq_items[i]);

    for (i = 0; i < kstruct->types_count; i++)
        g_clear_object(&kstruct->types[i]);

    for (i = 0; i < kstruct->instances_count; i++)
        g_clear_object(&kstruct->instances[i]);

    for (i = 0; i < kstruct->enums_count; i++)
        g_clear_object(&kstruct->enums[i]);

    G_OBJECT_CLASS(g_kaitai_structure_parent_class)->dispose(G_OBJECT(kstruct));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_structure_finalize(GKaitaiStruct *kstruct)
{
    if (kstruct->seq_items != NULL)
        free(kstruct->seq_items);

    if (kstruct->types != NULL)
        free(kstruct->types);

    if (kstruct->instances != NULL)
        free(kstruct->instances);

    if (kstruct->enums != NULL)
        free(kstruct->enums);

    G_OBJECT_CLASS(g_kaitai_structure_parent_class)->finalize(G_OBJECT(kstruct));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : text = définitions textuelles d'un contenu brut.             *
*                                                                             *
*  Description : Crée un nouvel interpréteur de structure Kaitai.             *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiStruct *g_kaitai_structure_new_from_text(const char *text)
{
    GKaitaiStruct *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_STRUCT, NULL);

    if (!g_kaitai_structure_create_from_text(result, text))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = lecteur de définition à initialiser pleinement.    *
*                text    = définitions textuelles d'un contenu brut.          *
*                                                                             *
*  Description : Met en place un interpréteur de définitions Kaitai.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_structure_create_from_text(GKaitaiStruct *kstruct, const char *text)
{
    bool result;                            /* Bilan à retourner           */
    GYamlNode *root;                        /* Noeud racine YAML           */

    root = parse_yaml_from_text(text, strlen(text));

    if (root != NULL)
    {
        result = g_kaitai_structure_create(kstruct, root);
        g_object_unref(G_OBJECT(root));
    }
    else
    {
        fprintf(stderr, "The provided YAML content seems invalid");
        result = false;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin vers des définitions de règles.            *
*                                                                             *
*  Description : Crée un nouvel interpréteur de structure Kaitai.             *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiStruct *g_kaitai_structure_new_from_file(const char *filename)
{
    GKaitaiStruct *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_STRUCT, NULL);

    if (!g_kaitai_structure_create_from_file(result, filename))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct  = lecteur de définition à initialiser pleinement.   *
*                filename = chemin vers des définitions de règles.            *
*                                                                             *
*  Description : Met en place un interpréteur de définitions Kaitai.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_structure_create_from_file(GKaitaiStruct *kstruct, const char *filename)
{
    bool result;                            /* Bilan à retourner           */
    GYamlNode *root;                        /* Noeud racine YAML           */

    root = parse_yaml_from_file(filename);

    if (root != NULL)
    {
        result = g_kaitai_structure_create(kstruct, root);
        g_object_unref(G_OBJECT(root));
    }
    else
    {
        fprintf(stderr, "The provided YAML content seems invalid");
        result = false;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = lecteur de définition à initialiser pleinement.    *
*                parent  = noeud Yaml contenant l'attribut à constituer.      *
*                                                                             *
*  Description : Met en place un lecteur de définitions Kaitai.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_structure_create(GKaitaiStruct *kstruct, GYamlNode *parent)
{
    bool result;                            /* Bilan à retourner           */
    GYamlNode *collec;                      /* Liste de noeuds à traiter   */
    GYamlNode **nodes;                      /* Eventuels noeuds trouvés    */
    size_t count;                           /* Quantité de ces noeuds      */
    size_t i;                               /* Boucle de parcours          */
    bool failed;                            /* Détection d'un échec        */

    result = false;

    /* Informations générales */

    kstruct->meta = g_kaitai_meta_new(parent);
    assert(kstruct->meta != NULL);

    /* Séquence */

    collec = g_yaml_node_find_first_by_path(parent, "/seq/");

    if (collec != NULL)
    {
        if (G_IS_YAML_COLLEC(collec))
            nodes = g_yaml_collection_get_nodes(G_YAML_COLLEC(collec), &count);
        else
            count = 0;

        if (count > 0)
        {
            kstruct->seq_items = calloc(count, sizeof(GKaitaiAttribute *));
            kstruct->seq_items_count = count;

            for (i = 0; i < count; i++)
            {
                kstruct->seq_items[i] = g_kaitai_attribute_new(nodes[i]);
                if (kstruct->seq_items[i] == NULL) break;

                g_object_unref(G_OBJECT(nodes[i]));

            }

            failed = (i < count);

            for (; i < count; i++)
                g_object_unref(G_OBJECT(nodes[i]));

            free(nodes);

            if (failed)
                goto bad_loading;

        }

        g_object_unref(G_OBJECT(collec));

    }

    /* Types particuliers éventuels */

    collec = g_yaml_node_find_first_by_path(parent, "/types/");

    if (collec != NULL)
    {
        if (G_IS_YAML_COLLEC(collec))
            nodes = g_yaml_collection_get_nodes(G_YAML_COLLEC(collec), &count);
        else
            count = 0;

        if (count > 0)
        {
            kstruct->types = calloc(count, sizeof(GKaitaiType *));
            kstruct->types_count = count;

            for (i = 0; i < count; i++)
            {
                kstruct->types[i] = g_kaitai_type_new(nodes[i]);
                if (kstruct->types[i] == NULL) break;

                g_object_unref(G_OBJECT(nodes[i]));

            }

            failed = (i < count);

            for (; i < count; i++)
                g_object_unref(G_OBJECT(nodes[i]));

            free(nodes);

            if (failed)
                goto bad_loading;

        }

        g_object_unref(G_OBJECT(collec));

    }

    /* Instances éventuelles */

    collec = g_yaml_node_find_first_by_path(parent, "/instances/");

    if (collec != NULL)
    {
        if (G_IS_YAML_COLLEC(collec))
            nodes = g_yaml_collection_get_nodes(G_YAML_COLLEC(collec), &count);
        else
            count = 0;

        if (count > 0)
        {
            kstruct->instances = calloc(count, sizeof(GKaitaiInstance *));
            kstruct->instances_count = count;

            for (i = 0; i < count; i++)
            {
                kstruct->instances[i] = g_kaitai_instance_new(nodes[i]);
                if (kstruct->instances[i] == NULL) break;

                g_object_unref(G_OBJECT(nodes[i]));

            }

            failed = (i < count);

            for (; i < count; i++)
                g_object_unref(G_OBJECT(nodes[i]));

            free(nodes);

            if (failed)
                goto bad_loading;

        }

        g_object_unref(G_OBJECT(collec));

    }

    /* Enumérations éventuelles */

    collec = g_yaml_node_find_first_by_path(parent, "/enums/");

    if (collec != NULL)
    {
        if (G_IS_YAML_COLLEC(collec))
            nodes = g_yaml_collection_get_nodes(G_YAML_COLLEC(collec), &count);
        else
            count = 0;

        if (count > 0)
        {
            kstruct->enums = calloc(count, sizeof(GKaitaiEnum *));
            kstruct->enums_count = count;

            for (i = 0; i < count; i++)
            {
                kstruct->enums[i] = g_kaitai_enum_new(nodes[i]);
                if (kstruct->enums[i] == NULL) break;

                g_object_unref(G_OBJECT(nodes[i]));

            }

            failed = (i < count);

            for (; i < count; i++)
                g_object_unref(G_OBJECT(nodes[i]));

            free(nodes);

            if (failed)
                goto bad_loading;

        }

        g_object_unref(G_OBJECT(collec));

    }

    /* Sortie heureuse */

    result = true;

 bad_loading:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = structure Kaitai à consulter.                      *
*                                                                             *
*  Description : Fournit la description globale d'une définition Kaitai.      *
*                                                                             *
*  Retour      : Description de la définition Kaitai courante.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiMeta *g_kaitai_structure_get_meta(const GKaitaiStruct *kstruct)
{
    GKaitaiMeta *result;                    /* Informations à retourner    */ 

    result = kstruct->meta;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = structure Kaitai en cours de parcours.             *
*                name    = désignation principale des énumérations ciblées.   *
*                                                                             *
*  Description : Fournit un ensemble d'énumérations locales de la structure.  *
*                                                                             *
*  Retour      : Enumérations locales ou NULL si non trouvée.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiEnum *g_kaitai_structure_get_enum(const GKaitaiStruct *kstruct, const sized_string_t *name)
{
    GKaitaiEnum *result;                    /* Instance à retourner        */
    size_t i;                               /* Boucle de parcours          */
    const char *other;                      /* Autre désignation à comparer*/

    result = NULL;

    for (i = 0; i < kstruct->enums_count; i++)
    {
        other = g_kaitai_enum_get_name(kstruct->enums[i]);

        if (strncmp(name->data, other, name->len) == 0) // FIXME
        {
            result = kstruct->enums[i];
            g_object_ref(G_OBJECT(result));
            break;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = structure Kaitai en cours de parcours.             *
*                name    = désignation du type particulier ciblé.             *
*                                                                             *
*  Description : Recherche la définition d'un type nouveau pour Kaitai.       *
*                                                                             *
*  Retour      : Type prêt à emploi ou NULL si non trouvé.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiType *g_kaitai_structure_find_sub_type(const GKaitaiStruct *kstruct, const char *name)
{
    GKaitaiType *result;                    /* Instance à retourner        */
    size_t i;                               /* Boucle de parcours          */
    const char *other;                      /* Autre désignation à comparer*/

    result = NULL;

    for (i = 0; i < kstruct->types_count; i++)
    {
        other = g_kaitai_type_get_name(kstruct->types[i]);

        if (strcmp(name, other) == 0)
        {
            result = kstruct->types[i];
            g_object_ref(G_OBJECT(result));
            break;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = structure Kaitai en cours de parcours.             *
*                content = contenu binaire en cours de traitement.            *
*                                                                             *
*  Description : Parcourt un contenu binaire selon une description Kaitai.    *
*                                                                             *
*  Retour      : Arborescence d'éléments rencontrés selon les spécifications. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMatchRecord *g_kaitai_structure_parse(GKaitaiStruct *kstruct, GBinContent *content)
{
    GMatchRecord *result;                   /* Arborescence à retourner    */ 
    vmpa2t pos;                             /* Tête de lecture             */
    kaitai_scope_t locals;                  /* Variables locales           */
    bool status;                            /* Bilan de l'analyse          */

    g_binary_content_compute_start_pos(content, &pos);

    init_record_scope(&locals, kstruct->meta);

    status = g_kaitai_parser_parse_content(G_KAITAI_PARSER(kstruct), &locals, content, &pos, &result);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : kstruct = structure Kaitai en cours de parcours.             *
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

static bool g_kaitai_structure_parse_content(GKaitaiStruct *kstruct, kaitai_scope_t *locals, GBinContent *content, vmpa2t *pos, GMatchRecord **record)
{
    bool result;                            /* Bilan à retourner           */
    GRecordGroup *group;                    /* Ensemble à constituer       */
    GMatchRecord *old;                      /* Sauvegarde de valeur        */
    size_t i;                               /* Boucle de parcours          */
    GMatchRecord *child;                    /* Nouvel élément mis en place */

    result = true;

    /* Si le groupe est vide */
    if ((kstruct->seq_items_count + kstruct->instances_count) == 0)
    {
        *record = G_MATCH_RECORD(g_record_empty_new(G_KAITAI_PARSER(kstruct), content, pos));

        if (locals->root == NULL)
            locals->root = *record;

    }

    /* Sinon on construit selon les définitions fournies */
    else
    {
        group = g_record_group_new(kstruct, content);
        *record = G_MATCH_RECORD(group);

        if (locals->root == NULL)
            locals->root = *record;

        old = locals->parent;
        locals->parent = *record;

        for (i = 0; i < kstruct->seq_items_count; i++)
        {
            result = g_kaitai_parser_parse_content(G_KAITAI_PARSER(kstruct->seq_items[i]),
                                                   locals, content, pos, &child);
            if (!result) goto exit;

            if (child != NULL)
            {
                g_record_group_add_record(group, child);
                g_object_unref(G_OBJECT(child));
            }

        }

        for (i = 0; i < kstruct->instances_count; i++)
        {
            result = g_kaitai_parser_parse_content(G_KAITAI_PARSER(kstruct->instances[i]),
                                                   locals, content, pos, &child);
            if (!result) goto exit;

            if (child != NULL)
            {
                g_record_group_add_record(group, child);
                g_object_unref(G_OBJECT(child));
            }

        }

 exit:

        locals->parent = old;

    }

    return result;

}
