
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cse.c - manipulation des types classes / structures / énumérations
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#include "cse.h"


#include <malloc.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/leb128.h"



/* Description de type classe/structure et énumération (instance) */
struct _GClassEnumType
{
    GDataType parent;                       /* A laisser en premier        */

    ClassEnumKind kind;                     /* Type représenté si connu    */
    char *name;                             /* Description humaine         */

};

/* Description de type classe/structure et énumération (classe) */
struct _GClassEnumTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des types classe ou assimilés. */
static void g_class_enum_type_class_init(GClassEnumTypeClass *);

/* Initialise l'instance d'un type classe ou assimilé. */
static void g_class_enum_type_init(GClassEnumType *);

/* Supprime toutes les références externes. */
static void g_class_enum_type_dispose(GClassEnumType *);

/* Procède à la libération totale de la mémoire. */
static void g_class_enum_type_finalize(GClassEnumType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_class_enum_type_load(GClassEnumType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_class_enum_type_store(const GClassEnumType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_class_enum_type_hash(const GClassEnumType *);

/* Crée un copie d'un type existant. */
static GDataType *g_class_enum_type_dup(const GClassEnumType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_class_enum_type_to_string(const GClassEnumType *, bool);



/* Indique le type défini pour un type classe ou assimilé. */
G_DEFINE_TYPE(GClassEnumType, g_class_enum_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types classe ou assimilés.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_class_enum_type_class_init(GClassEnumTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_class_enum_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_class_enum_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_class_enum_type_load;
    type->store = (type_store_fc)g_class_enum_type_store;

    type->hash = (type_hash_fc)g_class_enum_type_hash;
    type->dup = (type_dup_fc)g_class_enum_type_dup;
    type->to_string = (type_to_string_fc)g_class_enum_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type classe ou assimilé.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_class_enum_type_init(GClassEnumType *type)
{
    type->kind = CEK_COUNT;
    type->name = NULL;

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

static void g_class_enum_type_dispose(GClassEnumType *type)
{
    G_OBJECT_CLASS(g_class_enum_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_class_enum_type_finalize(GClassEnumType *type)
{
    if (type->name != NULL)
        free(type->name);

    G_OBJECT_CLASS(g_class_enum_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : kind = type de structure à représenter.                      *
*                name = désignation humaine du type.                          *
*                                                                             *
*  Description : Crée une représentation de classe, structure ou énumération. *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_class_enum_type_new(ClassEnumKind kind, char *name)
{
    GClassEnumType *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_CLASS_ENUM_TYPE, NULL);

    result->kind = kind;
    result->name = name;

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

static bool g_class_enum_type_load(GClassEnumType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = G_DATA_TYPE_CLASS(g_class_enum_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->kind = value;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->name = calloc(value, sizeof(char));
    result = extract_packed_buffer(pbuf, type->name, value, false);

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

static bool g_class_enum_type_store(const GClassEnumType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t len;                             /* Taille d'une chaîne         */

    result = G_DATA_TYPE_CLASS(g_class_enum_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = pack_uleb128((uleb128_t []){ g_class_enum_type_get_kind(type) }, pbuf);
    if (!result) goto exit;

    len = strlen(type->name);

    result = pack_uleb128((uleb128_t []){ len }, pbuf);
    if (!result) goto exit;

    result = extend_packed_buffer(pbuf, type->name, len, false);

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

static guint g_class_enum_type_hash(const GClassEnumType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    result = g_int_hash((gint []){ g_class_enum_type_get_kind(type) });

    result ^= g_str_hash(type->name);

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

static GDataType *g_class_enum_type_dup(const GClassEnumType *type)
{
    GDataType *result;                      /* Copie à retourner           */
    char *name;                             /* Nouveau nom copié           */

    name = (type->name != NULL ? strdup(type->name) : NULL);

    result = g_class_enum_type_new(type->kind, name);

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

static char *g_class_enum_type_to_string(const GClassEnumType *type, bool include)
{
    char *result;                           /* Valeur à renvoyer           */

    switch (type->kind)
    {
        case CEK_VIRTUAL_TABLE:
            result = strdup("vtable");
            break;

        case CEK_VIRTUAL_STRUCT:
            result = strdup("vstruct");
            break;

        default:
            result = (type->name != NULL ? strdup(type->name) : NULL);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type pris en compte géré par le type.             *
*                                                                             *
*  Retour      : Type pris en compte.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ClassEnumKind g_class_enum_type_get_kind(const GClassEnumType *type)
{
    ClassEnumKind result;                   /* Type de base à renvoyer     */

    result = type->kind;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Donne la désignation de la classe / structure / énumération. *
*                                                                             *
*  Retour      : Chaîne de caractères.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_class_enum_type_get_name(const GClassEnumType *type)
{
    char *result;                           /* Valeur à renvoyer           */

    result = type->name;

    return result;

}
