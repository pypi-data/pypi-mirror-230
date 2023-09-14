
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.c - manipulation des types de tableaux
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


#include "array.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/extstr.h"
#include "../../common/leb128.h"



/* Description de tableau (instance) */
struct _GArrayType
{
    GDataType parent;                       /* A laisser en premier        */

    bool numbered;                          /* Dimension chiffrée ?        */

    union
    {
        ssize_t dim_number;                 /* Taille en chiffre           */
        char *dim_expr;                     /* Taille via expression       */

    };

    GDataType *members;                     /* Type des membres            */

};

/* Description de tableau (classe) */
struct _GArrayTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des tableaux. */
static void g_array_type_class_init(GArrayTypeClass *);

/* Initialise l'instance d'un tableau. */
static void g_array_type_init(GArrayType *);

/* Supprime toutes les références externes. */
static void g_array_type_dispose(GArrayType *);

/* Procède à la libération totale de la mémoire. */
static void g_array_type_finalize(GArrayType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_array_type_load(GArrayType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_array_type_store(const GArrayType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_array_type_hash(const GArrayType *);

/* Crée un copie d'un type existant. */
static GDataType *g_array_type_dup(const GArrayType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_array_type_to_string(const GArrayType *, bool);



/* Indique le type défini pour un tableau. */
G_DEFINE_TYPE(GArrayType, g_array_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tableaux.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_array_type_class_init(GArrayTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_array_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_array_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_array_type_load;
    type->store = (type_store_fc)g_array_type_store;

    type->hash = (type_hash_fc)g_array_type_hash;
    type->dup = (type_dup_fc)g_array_type_dup;
    type->to_string = (type_to_string_fc)g_array_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un tableau.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_array_type_init(GArrayType *type)
{
    type->numbered = true;

    type->dim_number = -1;

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

static void g_array_type_dispose(GArrayType *type)
{
    g_clear_object(&type->members);

    G_OBJECT_CLASS(g_array_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_array_type_finalize(GArrayType *type)
{
    if (!type->numbered && type->dim_expr != NULL)
        free(type->dim_expr);

    G_OBJECT_CLASS(g_array_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : members = type des membres du tableau.                       *
*                                                                             *
*  Description : Crée une représentation de tableau.                          *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_array_type_new(GDataType *members)
{
    GArrayType *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARRAY_TYPE, NULL);

    result->members = members;

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

static bool g_array_type_load(GArrayType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    bool numbered;                          /* Choix de la dimension       */
    leb128_t number;                        /* Valeur LEB128 à charger     */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = G_DATA_TYPE_CLASS(g_array_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = extract_packed_buffer(pbuf, &numbered, sizeof(uint8_t), false);
    if (!result) goto exit;

    type->numbered = (numbered == 0x01);

    if (type->numbered)
    {
        result = unpack_leb128(&number, pbuf);
        if (!result) goto exit;

        type->dim_number = number;

    }
    else
    {
        result = unpack_uleb128(&value, pbuf);
        if (!result) goto exit;

        type->dim_expr = calloc(value, sizeof(char));
        result = extract_packed_buffer(pbuf, type->dim_expr, value, false);
        if (!result) goto exit;

    }

    type->members = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));
    result = (type->members != NULL);

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

static bool g_array_type_store(const GArrayType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t len;                             /* Taille d'une chaîne         */

    result = G_DATA_TYPE_CLASS(g_array_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = extend_packed_buffer(pbuf, (uint8_t []){ type->numbered ? 0x01 : 0x00 }, sizeof(uint8_t), false);
    if (!result) goto exit;

    if (type->numbered)
    {
        result = pack_leb128((leb128_t []){ type->dim_number }, pbuf);
        if (!result) goto exit;

    }
    else
    {
        len = strlen(type->dim_expr);

        result = pack_uleb128((uleb128_t []){ len }, pbuf);
        if (!result) goto exit;

        result = extend_packed_buffer(pbuf, type->dim_expr, len, false);
        if (!result) goto exit;

    }

    result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->members), pbuf);

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

static guint g_array_type_hash(const GArrayType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    if (type->numbered)
        result = g_int_hash((gint []){ type->dim_number });
    else
        result = g_str_hash(type->dim_expr);

    result ^= g_data_type_hash(type->members);

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

static GDataType *g_array_type_dup(const GArrayType *type)
{
    GDataType *result;                      /* Nouvelle instance à renvoyer*/
    GDataType *members;                     /* Copie du type interne       */

    members = g_data_type_dup(type->members);
    result = g_array_type_new(members);

    if (type->numbered)
        g_array_type_set_dimension_number(G_ARRAY_TYPE(result), type->dim_number);

    else if (type->dim_expr != NULL)
        g_array_type_set_dimension_expression(G_ARRAY_TYPE(result), strdup(type->dim_expr));

    else
        g_array_type_set_empty_dimension(G_ARRAY_TYPE(result));

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

static char *g_array_type_to_string(const GArrayType *type, bool include)
{
    char *result;                           /* Chaîne finale à renvoyer    */
    char *tmp;                              /* Transcription temporaire    */

    result = g_data_type_to_string(type->members, include);
    if (result == NULL) goto exit;

    result = stradd(result, "[");

    if (type->numbered)
    {
        if (type->dim_number != -1)
        {
            asprintf(&tmp, "%zd", type->dim_number);
            result = stradd(result, tmp);
            free(tmp);
        }
    }

    else if (type->dim_expr != NULL)
        result = stradd(result, type->dim_expr);

    result = stradd(result, "]");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type des membres du tableau.                      *
*                                                                             *
*  Retour      : Instance d'un autre type.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_array_type_get_members_type(const GArrayType *type)
{
    GDataType *result;                      /* Type à retourner            */

    result = type->members;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si la dimension du tableau est chiffrée.             *
*                                                                             *
*  Retour      : true si la dimension est chiffrée.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_array_type_is_dimension_numbered(const GArrayType *type)
{
    bool result;                            /* Etat à retourner            */

    result = type->numbered;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : Dimension positive ou nulle.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ssize_t g_array_type_get_dimension_number(const GArrayType *type)
{
    ssize_t result;                         /* Taille à retourner          */

    assert(type->numbered);

    result = (type->numbered ? type->dim_number : 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à traiter.                                       *
*                dim  = dimension positive ou nulle.                          *
*                                                                             *
*  Description : Définit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_array_type_set_dimension_number(GArrayType *type, ssize_t dim)
{
    if (!type->numbered && type->dim_expr != NULL)
        free(type->dim_expr);

    type->numbered = true;

    type->dim_number = dim;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : Expression de dimension.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_array_type_get_dimension_expression(const GArrayType *type)
{
    char *result;                           /* Expression à retourner      */

    assert(!type->numbered);

    result = (type->numbered ? NULL : type->dim_expr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à traiter.                                       *
*                expr = expression de dimension.                              *
*                                                                             *
*  Description : Définit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_array_type_set_dimension_expression(GArrayType *type, char *expr)
{
    if (!type->numbered && type->dim_expr != NULL)
        free(type->dim_expr);

    type->numbered = false;

    type->dim_expr = expr;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à traiter.                                       *
*                                                                             *
*  Description : Définit une dimension vide pour le tableau.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_array_type_set_empty_dimension(GArrayType *type)
{
    if (!type->numbered && type->dim_expr != NULL)
        free(type->dim_expr);

    type->numbered = false;

    type->dim_expr = NULL;

}
