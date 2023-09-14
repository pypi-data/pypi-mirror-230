
/* Chrysalide - Outil d'analyse de fichiers binaires
 * basic.c - manipulation des types de données de base
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


#include "basic.h"


#include <assert.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/leb128.h"



/* Description de type basique (instance) */
struct _GBasicType
{
    GDataType parent;                       /* A laisser en premier        */

    BaseType type;                          /* Type représenté si connu    */

};

/* Description de type basique (classe) */
struct _GBasicTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des types basiques. */
static void g_basic_type_class_init(GBasicTypeClass *);

/* Initialise l'instance d'un type basique. */
static void g_basic_type_init(GBasicType *);

/* Supprime toutes les références externes. */
static void g_basic_type_dispose(GBasicType *);

/* Procède à la libération totale de la mémoire. */
static void g_basic_type_finalize(GBasicType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_basic_type_load(GBasicType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_basic_type_store(const GBasicType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_basic_type_hash(const GBasicType *);

/* Crée un copie d'un type existant. */
static GDataType *g_basic_type_dup(const GBasicType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_basic_type_to_string(const GBasicType *, bool);



/* Indique le type défini pour un type basique. */
G_DEFINE_TYPE(GBasicType, g_basic_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types basiques.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_basic_type_class_init(GBasicTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_basic_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_basic_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_basic_type_load;
    type->store = (type_store_fc)g_basic_type_store;

    type->hash = (type_hash_fc)g_basic_type_hash;
    type->dup = (type_dup_fc)g_basic_type_dup;
    type->to_string = (type_to_string_fc)g_basic_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type basique.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_basic_type_init(GBasicType *type)
{
    type->type = BTP_INVALID;

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

static void g_basic_type_dispose(GBasicType *type)
{
    G_OBJECT_CLASS(g_basic_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_basic_type_finalize(GBasicType *type)
{
    G_OBJECT_CLASS(g_basic_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type simple à représenter.                            *
*                                                                             *
*  Description : Crée une représentation de type basique.                     *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_basic_type_new(BaseType type)
{
    GBasicType *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_BASIC_TYPE, NULL);

    result->type = type;

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

static bool g_basic_type_load(GBasicType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = G_DATA_TYPE_CLASS(g_basic_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);

    if (result)
        result = unpack_uleb128(&value, pbuf);

    if (result)
        type->type = value;

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

static bool g_basic_type_store(const GBasicType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DATA_TYPE_CLASS(g_basic_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);

    if (result)
        result = pack_uleb128((uleb128_t []){ type->type }, pbuf);

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

static guint g_basic_type_hash(const GBasicType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    result = g_int_hash((gint []){ g_basic_type_get_base(type) });

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

static GDataType *g_basic_type_dup(const GBasicType *type)
{
    GDataType *result;                      /* Copie à retourner           */

    result = g_basic_type_new(type->type);

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

static char *g_basic_type_to_string(const GBasicType *type, bool include)
{
    const char *desc;                       /* Représentation à copier     */

    switch (type->type)
    {
        case BTP_VOID:
            desc = "void";
            break;

        case BTP_WCHAR_T:
            desc = "wchar_t";
            break;

        case BTP_BOOL:
            desc = "bool";
            break;

        case BTP_CHAR:
            desc = "char";
            break;

        case BTP_SCHAR:
            desc = "signed char";
            break;

        case BTP_UCHAR:
            desc = "unsigned char";
            break;

        case BTP_SHORT:
            desc = "short";
            break;

        case BTP_USHORT:
            desc = "unsigned short";
            break;

        case BTP_INT:
            desc = "int";
            break;

        case BTP_UINT:
            desc = "unsigned int";
            break;

        case BTP_LONG:
            desc = "long";
            break;

        case BTP_ULONG:
            desc = "unsigned long";
            break;

        case BTP_LONG_LONG:
            desc = "long long";
            break;

        case BTP_ULONG_LONG:
            desc = "unsigned long long";
            break;

        case BTP_INT128:
            desc = "__int128";
            break;

        case BTP_UINT128:
            desc = "unsigned __int128";
            break;

        case BTP_FLOAT:
            desc = "float";
            break;

        case BTP_DOUBLE:
            desc = "double";
            break;

        case BTP_LONG_DOUBLE:
            desc = "long double";
            break;

        case BTP_FLOAT128:
            desc = "__float128";
            break;

        case BTP_ELLIPSIS:
            desc = "...";
            break;

        case BTP_754R_64:
            desc = "__float754r_64";
            break;

        case BTP_754R_128:
            desc = "__float754r_128";
            break;

        case BTP_754R_32:
            desc = "__float754r_32";
            break;

        case BTP_754R_16:
            desc = "__float754r_16";
            break;

        case BTP_754R_N:
            desc = "__float754r_n";
            break;

        case BTP_CHAR32_T:
            desc = "char32_t";
            break;

        case BTP_CHAR16_T:
            desc = "char16_t";
            break;

        case BTP_AUTO:
            desc = "auto";
            break;

        case BTP_DECL_AUTO:
            desc = "decltype(auto)";
            break;

        default:
            assert(false);
            desc = NULL;
            break;

    }

    return (desc != NULL ? strdup(desc) : NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type de base géré par le type.                    *
*                                                                             *
*  Retour      : Type basique.                                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BaseType g_basic_type_get_base(const GBasicType *type)
{
    BaseType result;                        /* Type de base à retourner    */

    result = type->type;

    return result;

}
