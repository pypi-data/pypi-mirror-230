
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr.c - manipulation de types sous forme d'expressions
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "expr.h"


#include <malloc.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/leb128.h"



/* Description de type sous forme d'expressions (instance) */
struct _GExprType
{
    GDataType parent;                       /* A laisser en premier        */

    char *value;                            /* Valeur brute de l'expression*/

};

/* Description de type sous forme d'expressions (classe) */
struct _GExprTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des types sous forme d'expressions. */
static void g_expr_type_class_init(GExprTypeClass *);

/* Initialise l'instance d'un type sous forme d'expressions. */
static void g_expr_type_init(GExprType *);

/* Supprime toutes les références externes. */
static void g_expr_type_dispose(GExprType *);

/* Procède à la libération totale de la mémoire. */
static void g_expr_type_finalize(GExprType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_expr_type_load(GExprType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_expr_type_store(const GExprType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_expr_type_hash(const GExprType *);

/* Crée un copie d'un type existant. */
static GDataType *g_expr_type_dup(const GExprType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_expr_type_to_string(const GExprType *, bool);



/* Indique le type défini pour un type sous forme d'expressions. */
G_DEFINE_TYPE(GExprType, g_expr_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types sous forme d'expressions.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_expr_type_class_init(GExprTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_expr_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_expr_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_expr_type_load;
    type->store = (type_store_fc)g_expr_type_store;

    type->hash = (type_hash_fc)g_expr_type_hash;
    type->dup = (type_dup_fc)g_expr_type_dup;
    type->to_string = (type_to_string_fc)g_expr_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type sous forme d'expressions.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_expr_type_init(GExprType *type)
{
    type->value = NULL;

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

static void g_expr_type_dispose(GExprType *type)
{
    G_OBJECT_CLASS(g_expr_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_expr_type_finalize(GExprType *type)
{
    if (type->value != NULL)
        free(type->value);

    G_OBJECT_CLASS(g_expr_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur brute de l'expression.                        *
*                                                                             *
*  Description : Crée une représentation de type sous forme d'expressions.    *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_expr_type_new(const char *value)
{
    GExprType *result;                   /* Structure à retourner       */

    result = g_object_new(G_TYPE_EXPR_TYPE, NULL);

    result->value = strdup(value);

    return G_DATA_TYPE(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type    = type de données à constuire.                       *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Charge un objet depuis une mémoire tampon.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_expr_type_load(GExprType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = G_DATA_TYPE_CLASS(g_expr_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->value = calloc(value, sizeof(char));
    result = extract_packed_buffer(pbuf, type->value, value, false);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type    = type de données à consulter.                       *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un objet dans une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_expr_type_store(const GExprType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t len;                             /* Taille d'une chaîne         */

    result = G_DATA_TYPE_CLASS(g_expr_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    len = strlen(type->value);

    result = pack_uleb128((uleb128_t []){ len }, pbuf);
    if (!result) goto exit;

    result = extend_packed_buffer(pbuf, type->value, len, false);
    if (!result) goto exit;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Calcule une empreinte pour un type de données.               *
*                                                                             *
*  Retour      : Valeur arbitraire sur 32 bits, idéalement unique par type.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_expr_type_hash(const GExprType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    result = g_str_hash(type->value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à dupliquer.                                     *
*                                                                             *
*  Description : Crée un copie d'un type existant.                            *
*                                                                             *
*  Retour      : Nouvelle instance de type identique à celle fournie.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *g_expr_type_dup(const GExprType *type)
{
    GDataType *result;                      /* Copie à retourner           */

    result = g_expr_type_new(type->value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type    = type à convertir.                                  *
*                include = doit-on inclure les espaces de noms ?              *
*                                                                             *
*  Description : Décrit le type fourni sous forme de caractères.              *
*                                                                             *
*  Retour      : Chaîne à libérer de la mémoire après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_expr_type_to_string(const GExprType *type, bool include)
{
    char *result;                           /* Valeur à renvoyer           */

    result = strdup(type->value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit la valeur d'un type fourni sous forme de caractères. *
*                                                                             *
*  Retour      : Chaîne formant une expression.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_expr_type_get_value(const GExprType *type)
{
    char *result;                           /* Valeur à renvoyer           */

    result = type->value;

    return result;

}
