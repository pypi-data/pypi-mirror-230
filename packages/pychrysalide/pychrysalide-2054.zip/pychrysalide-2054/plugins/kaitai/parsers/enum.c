
/* Chrysalide - Outil d'analyse de fichiers binaires
 * enum.h - gestion des énumérations Kaitai
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


#include "enum.h"


#include <malloc.h>
#include <string.h>


#include <i18n.h>


#include <common/extstr.h>
#include <common/sort.h>
#include <core/logs.h>
#include <plugins/yaml/collection.h>
#include <plugins/yaml/pair.h>


#include "enum-int.h"



/* ------------------------- MANIPULATION D'UNE ENUMERATION ------------------------- */


/* Construit une valeur d'énumération à partir d'indications. */
static enum_value_t *build_enum_value(GYamlNode *, bool *);

/* Supprime de la mémoire une valeur d'énumération. */
static void delete_enum_value(enum_value_t *);

/* Etablit la comparaison entre deux valeurs d'énumération. */
static int compare_enum_values_by_value(const enum_value_t **, const enum_value_t **);

/* Etablit la comparaison entre deux noms d'énumération. */
static int compare_enum_values_by_label(const enum_value_t **, const enum_value_t **);

/* Etablit la comparaison entre deux noms d'énumération. */
static int compare_enum_values_by_sized_label(const sized_string_t *, const enum_value_t **);



/* ----------------------- GESTION D'UN GROUPE D'ENUMERATIONS ----------------------- */


/* Initialise la classe des groupes d'énumérations Kaitai. */
static void g_kaitai_enum_class_init(GKaitaiEnumClass *);

/* Initialise un groupe d'énumérations Kaitai. */
static void g_kaitai_enum_init(GKaitaiEnum *);

/* Supprime toutes les références externes. */
static void g_kaitai_enum_dispose(GKaitaiEnum *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_enum_finalize(GKaitaiEnum *);



/* ---------------------------------------------------------------------------------- */
/*                           MANIPULATION D'UNE ENUMERATION                           */
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

static enum_value_t *build_enum_value(GYamlNode *node, bool *defcase)
{
    enum_value_t *result;                   /* Valeur à retourner          */
    const char *key;                        /* Clef d'une énumération      */
    kaitai_scope_t fake;                    /* Contexte de circonstance    */
    resolved_value_t kval;                  /* Valeur à indexer            */
    const char *value;                      /* Valeur Yaml particulière    */
    char *path;                             /* Chemin d'accès suivant      */
    GYamlNode *children;                    /* Sous-noeuds rattachés       */
    GYamlNode *sub;                         /* Sous-noeud à considérer     */

    result = NULL;

    *defcase = false;

    if (!G_IS_YAML_PAIR(node))
        goto bad_node;

    /* Identification de la valeur énumérative */

    key = g_yaml_pair_get_key(G_YAML_PAIR(node));

    if (strcmp(key, "_") == 0)
    {
        /**
         * Exemple de choix par défaut :
         * http://doc.kaitai.io/user_guide.html#tlv
         */

        kval.type = GVT_UNSIGNED_INTEGER;
        kval.unsigned_integer = ~0llu;

        *defcase = true;

    }

    else
    {
        fake.meta =  NULL;
        fake.root =  NULL;
        fake.parent =  NULL;
        fake.last =  NULL;

        if (!resolve_kaitai_expression_as_integer(&fake, key, strlen(key), &kval))
            goto bad_node;

    }

    /* Récupération des éléments associés à la valeur */

    value = g_yaml_pair_get_value(G_YAML_PAIR(node));

    if (value != NULL)
    {
        result = malloc(sizeof(enum_value_t));

        result->value = kval;
        result->label = strdup(value);
        result->doc = NULL;

    }
    else
    {
        /**
         * Les énumérations peuvent comporter un commentaire associé
         * sous forme d'un élément de documentation complémentaire.
         *
         * Cf. http://doc.kaitai.io/user_guide.html#verbose-enums
         */

        asprintf(&path, "/%s/", key);
        children = g_yaml_node_find_first_by_path(node, path);
        free(path);

        if (!G_IS_YAML_COLLEC(children))
            goto bad_value;

        /* Identifiant */

        sub = g_yaml_node_find_first_by_path(children, "/id");

        if (!G_IS_YAML_PAIR(sub))
            goto bad_sub_value;

        value = g_yaml_pair_get_value(G_YAML_PAIR(sub));

        if (value == NULL)
            goto bad_sub_value;

        result = malloc(sizeof(enum_value_t));

        result->value = kval;
        result->label = strdup(value);
        result->doc = NULL;

        g_object_unref(G_OBJECT(sub));

        /* Documentation */

        sub = g_yaml_node_find_first_by_path(children, "/doc");

        if (!G_IS_YAML_PAIR(sub))
            goto bad_sub_value;

        value = g_yaml_pair_get_value(G_YAML_PAIR(sub));

        if (value == NULL)
            goto bad_sub_value;

        result->doc = strdup(value);

 bad_sub_value:

        g_clear_object(&sub);

        g_object_unref(G_OBJECT(children));

 bad_value:

        ;

    }

 bad_node:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur à traiter.                                    *
*                                                                             *
*  Description : Supprime de la mémoire une valeur d'énumération.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_enum_value(enum_value_t *value)
{
    EXIT_RESOLVED_VALUE(value->value);

    free(value->label);

    if (value->doc != NULL)
        free(value->doc);

    free(value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premières informations à consulter.                      *
*                b = secondes informations à consulter.                       *
*                                                                             *
*  Description : Etablit la comparaison entre deux valeurs d'énumération.     *
*                                                                             *
*  Retour      : Bilan : -1 (a < b), 0 (a == b) ou 1 (a > b).                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_enum_values_by_value(const enum_value_t **a, const enum_value_t **b)
{
    int result;                             /* Bilan à retourner           */
    const resolved_value_t *value_a;        /* Raccouri d'accès pour a     */
    const resolved_value_t *value_b;        /* Raccouri d'accès pour b     */

    value_a = &(*a)->value;
    value_b = &(*b)->value;

    if (value_a->type == GVT_UNSIGNED_INTEGER && value_b->type == GVT_UNSIGNED_INTEGER)
        result = sort_unsigned_long_long(value_a->unsigned_integer, value_b->unsigned_integer);

    else if (value_a->type == GVT_UNSIGNED_INTEGER && value_b->type == GVT_UNSIGNED_INTEGER)
        result = sort_signed_long_long(value_a->signed_integer, value_b->signed_integer);

    else
    {
        /**
         * Le code Python a deux options : soit fournir un équivalent à la
         * structure resolved_value_t lors de l'appel correspondant à cette
         * fonction compare_enum_values_by_value(), soit fournir un nombre
         * directement.
         *
         * Comme PyArg_ParseTuple() est obligée de trancher entre non-signé
         * et signé, le parti est pris de considérer le non-signé coté Python.
         * On s'adapte en conséquence ici.
         *
         * La structure resolved_value_t est une union, donc les valeurs
         * sont potientiellement au mauvais format mais bien présentes.
         */

        /**
         * result = sort_unsigned_long_long(value_a->type, value_b->type);
         */

        result = sort_unsigned_long_long(value_a->unsigned_integer, value_b->unsigned_integer);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premières informations à consulter.                      *
*                b = secondes informations à consulter.                       *
*                                                                             *
*  Description : Etablit la comparaison entre deux noms d'énumération.        *
*                                                                             *
*  Retour      : Bilan : -1 (a < b), 0 (a == b) ou 1 (a > b).                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_enum_values_by_label(const enum_value_t **a, const enum_value_t **b)
{
    int result;                             /* Bilan à retourner           */

    result = strcmp((*a)->label, (*b)->label);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : l = premières informations à consulter.                      *
*                b = secondes informations à consulter.                       *
*                                                                             *
*  Description : Etablit la comparaison entre deux noms d'énumération.        *
*                                                                             *
*  Retour      : Bilan : -1 (a < b), 0 (a == b) ou 1 (a > b).                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_enum_values_by_sized_label(const sized_string_t *l, const enum_value_t **b)
{
    int result;                             /* Bilan à retourner           */

    result = strncmp(l->data, (*b)->label, l->len);     // FIXME

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         GESTION D'UN GROUPE D'ENUMERATIONS                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un ensemble d'énumérations Kaitai. */
G_DEFINE_TYPE(GKaitaiEnum, g_kaitai_enum, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des groupes d'énumérations Kaitai.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_enum_class_init(GKaitaiEnumClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_enum_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_enum_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise un groupe d'énumérations Kaitai.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_enum_init(GKaitaiEnum *kenum)
{
    kenum->name = NULL;

    kenum->cases_v2l = NULL;
    kenum->cases_v2l_count = 0;

    kenum->cases_l2v = NULL;
    kenum->cases_l2v_count = 0;

    kenum->defcase = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_enum_dispose(GKaitaiEnum *kenum)
{
    G_OBJECT_CLASS(g_kaitai_enum_parent_class)->dispose(G_OBJECT(kenum));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_enum_finalize(GKaitaiEnum *kenum)
{
    size_t i;                               /* Boucle de parcours          */

    if (kenum->name != NULL)
        free(kenum->name);

    for (i = 0; i < kenum->cases_v2l_count; i++)
        delete_enum_value(kenum->cases_v2l[i]);

    if (kenum->cases_v2l != NULL)
        free(kenum->cases_v2l);

    if (kenum->cases_l2v != NULL)
        free(kenum->cases_l2v);

    if (kenum->defcase != NULL)
        delete_enum_value(kenum->defcase);

    G_OBJECT_CLASS(g_kaitai_enum_parent_class)->finalize(G_OBJECT(kenum));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Construit un groupe d'énumérations Kaitai.                   *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiEnum *g_kaitai_enum_new(GYamlNode *parent)
{
    GKaitaiEnum *result;                   /* Identifiant à retourner     */

    result = g_object_new(G_TYPE_KAITAI_ENUM, NULL);

    if (!g_kaitai_enum_create(result, parent))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum  = groupe d'énumérations à initialiser pleinement.     *
*                parent = noeud Yaml contenant l'attribut à constituer.       *
*                                                                             *
*  Description : Met en place un groupe d'énumérations Kaitai.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_enum_create(GKaitaiEnum *kenum, GYamlNode *parent)
{
    bool result;                            /* Bilan à retourner           */
    char *path;                             /* Chemin des valeurs          */
    GYamlNode *collec;                      /* Liste de noeuds à traiter   */
    GYamlNode **nodes;                      /* Eventuels noeuds trouvés    */
    size_t count;                           /* Quantité de ces noeuds      */
    size_t i;                               /* Boucle de parcours          */
    bool defcase;                           /* Définition par défaut ?     */
    enum_value_t *value;                    /* Valeur énumérative nouvelle */
    bool found;                             /* Présence de partage existant*/
    size_t index;                           /* Indice du point d'insertion */

    result = false;

    /* Récupération du nom */

    if (!G_IS_YAML_PAIR(parent)) goto exit;

    kenum->name = strdup(g_yaml_pair_get_key(G_YAML_PAIR(parent)));

    /* Association de valeurs */

    path = strdup("/");
    path = stradd(path, kenum->name);
    path = stradd(path, "/");

    collec = g_yaml_node_find_first_by_path(parent, path);

    free(path);

    if (collec != NULL)
    {
        if (G_IS_YAML_COLLEC(collec))
            nodes = g_yaml_collection_get_nodes(G_YAML_COLLEC(collec), &count);
        else
            count = 0;

        if (count > 0)
        {
            for (i = 0; i < count; i++)
            {
                value = build_enum_value(nodes[i], &defcase);
                if (value == NULL) break;

                if (defcase)
                {
                    if (kenum->defcase != NULL)
                    {
                        log_variadic_message(LMT_WARNING,
                                             _("Multiple definition of the defaut value for the enumeration '%s'"),
                                             kenum->name);

                        delete_enum_value(value);
                        break;

                    }

                    /**
                     * Exemple de choix par défaut :
                     * http://doc.kaitai.io/user_guide.html#tlv
                     */

                    kenum->defcase = value;

                }

                else
                {
                    kenum->cases_v2l = qinsert(kenum->cases_v2l, &kenum->cases_v2l_count, sizeof(enum_value_t *),
                                               (__compar_fn_t)compare_enum_values_by_value, &value);

                    found = bsearch_index(&value, kenum->cases_l2v, kenum->cases_l2v_count, sizeof(enum_value_t *),
                                          (__compar_fn_t)compare_enum_values_by_label, &index);

                    if (found)
                        log_variadic_message(LMT_WARNING,
                                             _("Multiple occurrence of the label %s in the enumeration '%s'"),
                                             value->label, kenum->name);

                    else
                        kenum->cases_l2v = _qinsert(kenum->cases_l2v, &kenum->cases_l2v_count, sizeof(enum_value_t *),
                                                    &value, index);

                }

                g_object_unref(G_OBJECT(nodes[i]));

            }

            result = (i == count);

            for (; i < count; i++)
                g_object_unref(G_OBJECT(nodes[i]));

            free(nodes);

        }

        g_object_unref(G_OBJECT(collec));

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum = groupe d'énumérations à consulter.                   *
*                                                                             *
*  Description : Fournit le nom principal d'une énumération.                  *
*                                                                             *
*  Retour      : Désignation de l'énumération.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_kaitai_enum_get_name(const GKaitaiEnum *kenum)
{
    const char *result;                     /* Chaîne à retourner          */

    result = kenum->name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum = groupe d'énumérations à consulter.                   *
*                label = étiquette de l'élément constant à traduire.          *
*                value = valeur concrète correspondante. [OUT]                *
*                                                                             *
*  Description : Traduit une étiquette brute en constante d'énumération.      *
*                                                                             *
*  Retour      : Bilan de la conversion.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_enum_find_value(const GKaitaiEnum *kenum, const sized_string_t *label, resolved_value_t *value)
{
    bool result;                            /* Présence à retourner        */
    size_t index;                           /* Indice du point d'insertion */

    result = bsearch_index(label, kenum->cases_l2v, kenum->cases_l2v_count, sizeof(enum_value_t *),
                           (__compar_fn_t)compare_enum_values_by_sized_label, &index);

    if (result)
        *value = kenum->cases_l2v[index]->value;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum  = groupe d'énumérations à consulter.                  *
*                value  = valeur concrète à transformer.                      *
*                prefix = détermine l'ajout d'un préfixe éventuel.            *
*                                                                             *
*  Description : Traduit une constante d'énumération en étiquette brute.      *
*                                                                             *
*  Retour      : Désignation ou NULL en cas d'échec.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_kaitai_enum_find_label(const GKaitaiEnum *kenum, const resolved_value_t *value, bool prefix)
{
    char *result;                           /* Etiquette à retourner       */
    enum_value_t faked;                     /* Copie d'élément recherché   */
    bool found;                             /* Présence de partage existant*/
    size_t index;                           /* Indice du point d'insertion */
    const enum_value_t *item;               /* Elément retrouvé par valeur */

    faked.value = *value;

    found = bsearch_index(&faked, kenum->cases_v2l, kenum->cases_v2l_count, sizeof(enum_value_t *),
                          (__compar_fn_t)compare_enum_values_by_value, &index);

    if (found)
        item = kenum->cases_l2v[index];
    else
        item = kenum->defcase;

    if (item != NULL)
    {
        if (prefix)
            asprintf(&result, "%s::%s", kenum->name, item->label);
        else
            result = strdup(item->label);
    }

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kenum = groupe d'énumérations à consulter.                   *
*                value = valeur concrète à transformer.                       *
*                                                                             *
*  Description : Traduit une constante d'énumération en documentation.        *
*                                                                             *
*  Retour      : Documentation associée à la valeur indiquée ou NULL.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_kaitai_enum_find_documentation(const GKaitaiEnum *kenum, const resolved_value_t *value)
{
    char *result;                           /* Documentation à retourner   */
    enum_value_t faked;                     /* Copie d'élément recherché   */
    bool found;                             /* Présence de partage existant*/
    size_t index;                           /* Indice du point d'insertion */
    const enum_value_t *item;               /* Elément retrouvé par valeur */

    faked.value = *value;

    found = bsearch_index(&faked, kenum->cases_v2l, kenum->cases_v2l_count, sizeof(enum_value_t *),
                          (__compar_fn_t)compare_enum_values_by_value, &index);

    if (found)
        item = kenum->cases_l2v[index];
    else
        item = kenum->defcase;

    if (item != NULL)
        result = strdup(item->doc);
    else
        result = NULL;

    return result;

}
