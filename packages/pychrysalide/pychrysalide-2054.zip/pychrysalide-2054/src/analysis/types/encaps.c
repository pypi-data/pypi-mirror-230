
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encaps.c - manipulation des types de données encapsulés
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


#include "encaps.h"


#include <assert.h>
#include <malloc.h>


#include "../type-int.h"
#include "../../common/extstr.h"
#include "../../common/leb128.h"



/* Description de type encapsulé (instance) */
struct _GEncapsulatedType
{
    GDataType parent;                       /* A laisser en premier        */

    EncapsulationType type;                 /* Encapsulation utilisée      */
    GDataType *child;                       /* Sous-type encadré           */

    size_t dimension;                       /* Dimension quand applicable  */

};

/* Description de type encapsulé (classe) */
struct _GEncapsulatedTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des types encapsulés. */
static void g_encapsulated_type_class_init(GEncapsulatedTypeClass *);

/* Initialise l'instance d'un type encapsulé. */
static void g_encapsulated_type_init(GEncapsulatedType *);

/* Supprime toutes les références externes. */
static void g_encapsulated_type_dispose(GEncapsulatedType *);

/* Procède à la libération totale de la mémoire. */
static void g_encapsulated_type_finalize(GEncapsulatedType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_encapsulated_type_load(GEncapsulatedType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_encapsulated_type_store(const GEncapsulatedType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_encapsulated_type_hash(const GEncapsulatedType *);

/* Crée un copie d'un type existant. */
static GDataType *g_encapsulated_type_dup(const GEncapsulatedType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_encapsulated_type_to_string(const GEncapsulatedType *, bool);

/* Indique si le type est un pointeur. */
static bool g_encapsulated_type_is_pointer(const GEncapsulatedType *);

/* Indique si le type est une référence. */
static bool g_encapsulated_type_is_reference(const GEncapsulatedType *);



/* Indique le type défini pour un type encapsulé. */
G_DEFINE_TYPE(GEncapsulatedType, g_encapsulated_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types encapsulés.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_encapsulated_type_class_init(GEncapsulatedTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_encapsulated_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_encapsulated_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_encapsulated_type_load;
    type->store = (type_store_fc)g_encapsulated_type_store;

    type->hash = (type_hash_fc)g_encapsulated_type_hash;
    type->dup = (type_dup_fc)g_encapsulated_type_dup;
    type->to_string = (type_to_string_fc)g_encapsulated_type_to_string;

    type->is_pointer = (type_is_pointer_fc)g_encapsulated_type_is_pointer;
    type->is_reference = (type_is_reference_fc)g_encapsulated_type_is_reference;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type encapsulé.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_encapsulated_type_init(GEncapsulatedType *type)
{
    type->type = ECT_COUNT;
    type->child = NULL;

    type->dimension = 0;

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

static void g_encapsulated_type_dispose(GEncapsulatedType *type)
{
    g_clear_object(&type->child);

    G_OBJECT_CLASS(g_encapsulated_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_encapsulated_type_finalize(GEncapsulatedType *type)
{
    G_OBJECT_CLASS(g_encapsulated_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type d'extension à représenter.                      *
*                child = base dont on doit dériver.                           *
*                                                                             *
*  Description : Crée une représentation de variable dérivée.                 *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_encapsulated_type_new(EncapsulationType type, GDataType *child)
{
    GEncapsulatedType *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_ENCAPSULATED_TYPE, NULL);

    result->type = type;
    result->child = child;

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

static bool g_encapsulated_type_load(GEncapsulatedType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = G_DATA_TYPE_CLASS(g_encapsulated_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->type = value;

    type->child = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));
    result = (type->child != NULL);
    if (!result) goto exit;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->dimension = value;

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

static bool g_encapsulated_type_store(const GEncapsulatedType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DATA_TYPE_CLASS(g_encapsulated_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = pack_uleb128((uleb128_t []){ g_encapsulated_type_get_etype(type) }, pbuf);
    if (!result) goto exit;

    result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->child), pbuf);
    if (!result) goto exit;

    result = pack_uleb128((uleb128_t []){ type->dimension }, pbuf);

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

static guint g_encapsulated_type_hash(const GEncapsulatedType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    result = g_int_hash((gint []){ g_encapsulated_type_get_etype(type) });

    result ^= g_data_type_hash(type->child);

    result ^= g_int_hash((gint []){ g_encapsulated_type_get_dimension(type) });

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

static GDataType *g_encapsulated_type_dup(const GEncapsulatedType *type)
{
    GDataType *result;                      /* Nouvelle instance à renvoyer*/
    GDataType *child;                       /* Copie du type interne       */

    child = g_data_type_dup(type->child);
    result = g_encapsulated_type_new(type->type, child);

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

static char *g_encapsulated_type_to_string(const GEncapsulatedType *type, bool include)
{
    char *result;                           /* Chaîne finale à renvoyer    */
    size_t i;                               /* Boucle de parcours          */

    result = g_data_type_to_string(type->child, include);
    if (result == NULL) goto exit;

    switch (type->type)
    {
        case ECT_POINTER:
            if (!g_data_type_is_pointer(type->child))
                result = stradd(result, " ");
            result = stradd(result, "*");
            break;

        case ECT_ARRAY:
            result = stradd(result, " ");
            for (i = 0; i < type->dimension; i++)
                result = stradd(result, "[]");
            break;

        case ECT_REFERENCE:
            if (!g_data_type_is_reference(type->child))
                result = stradd(result, " ");
            result = stradd(result, "&");
            break;

        case ECT_RVALUE_REF:
            if (!g_data_type_is_reference(type->child))
                result = stradd(result, " ");
            result = stradd(result, "&&");
            break;

        case ECT_COMPLEX:
            result = stradd(result, " complex");
            break;

        case ECT_IMAGINARY:
            result = stradd(result, " imaginary");
            break;

        default:
            assert(false);
            free(result);
            result = NULL;
            break;

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si le type est un pointeur.                          *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_encapsulated_type_is_pointer(const GEncapsulatedType *type)
{
    bool result;                            /* Bilan à retourner           */

    result = (type->type == ECT_POINTER);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si le type est une référence.                        *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_encapsulated_type_is_reference(const GEncapsulatedType *type)
{
    bool result;                            /* Bilan à retourner           */

    result = (type->type == ECT_REFERENCE || type->type == ECT_RVALUE_REF);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type d'encapsulation gérée par le type.           *
*                                                                             *
*  Retour      : Type d'encapsulation gérée.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

EncapsulationType g_encapsulated_type_get_etype(const GEncapsulatedType *type)
{
    return type->type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type encapsulée dans le type.                     *
*                                                                             *
*  Retour      : Sous-type encapsulé dans le type.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_encapsulated_type_get_item(const GEncapsulatedType *type)
{
    GDataType *result;                      /* Type à retourner            */

    result = type->child;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit la dimension éventuellement associée au type.        *
*                                                                             *
*  Retour      : Dimension positive ou nulle.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_encapsulated_type_get_dimension(const GEncapsulatedType *type)
{
    return type->dimension;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                dim  = dimension positive ou nulle.                          *
*                                                                             *
*  Description : Définit la dimension éventuellement associée au type.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_encapsulated_type_set_dimension(GEncapsulatedType *type, size_t dim)
{
    type->dimension = dim;

}
