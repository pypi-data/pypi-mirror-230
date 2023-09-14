
/* Chrysalide - Outil d'analyse de fichiers binaires
 * override.c - manipulation des types pointant sur une fonction virtuelle
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


#include "override.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/extstr.h"
#include "../../common/leb128.h"



/* Description de fonction virtuelle (instance) */
struct _GOverrideType
{
    GDataType parent;                       /* A laisser en premier        */

    GDataType *base;                        /* Type de base à traiter      */
    call_offset_t offsets[2];               /* Décalages à appliquer       */
    bool with_covariant;                    /* Variation avec covariant    */

};

/* Description de fonction virtuelle (classe) */
struct _GOverrideTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des fonctions virtuelles. */
static void g_override_type_class_init(GOverrideTypeClass *);

/* Initialise l'instance d'une fonction virtuelle. */
static void g_override_type_init(GOverrideType *);

/* Supprime toutes les références externes. */
static void g_override_type_dispose(GOverrideType *);

/* Procède à la libération totale de la mémoire. */
static void g_override_type_finalize(GOverrideType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_override_type_load(GOverrideType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_override_type_store(const GOverrideType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_override_type_hash(const GOverrideType *);

/* Crée un copie d'un type existant. */
static GDataType *g_override_type_dup(const GOverrideType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_override_type_to_string(const GOverrideType *, bool);



/* Indique le type défini pour une fonction virtuelle. */
G_DEFINE_TYPE(GOverrideType, g_override_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des fonctions virtuelles.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_override_type_class_init(GOverrideTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_override_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_override_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_override_type_load;
    type->store = (type_store_fc)g_override_type_store;

    type->hash = (type_hash_fc)g_override_type_hash;
    type->dup = (type_dup_fc)g_override_type_dup;
    type->to_string = (type_to_string_fc)g_override_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'une fonction virtuelle.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_override_type_init(GOverrideType *type)
{
    type->base = NULL;
    memset(type->offsets, 0, sizeof(type->offsets));
    type->with_covariant = false;

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

static void g_override_type_dispose(GOverrideType *type)
{
    g_clear_object(&type->base);

    G_OBJECT_CLASS(g_override_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_override_type_finalize(GOverrideType *type)
{
    G_OBJECT_CLASS(g_override_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base   = type de base sur lequel s'appuyer.                  *
*                offset = décalage à appliquer.                               *
*                                                                             *
*  Description : Crée une représentation de fonction virtuelle.               *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_override_type_new(GDataType *base, const call_offset_t *offset)
{
    GOverrideType *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_OVERRIDE_TYPE, NULL);

    result->base = base;
    result->offsets[0] = *offset;
    result->with_covariant = false;

    return G_DATA_TYPE(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base = type de base sur lequel s'appuyer.                    *
*                off0 = premier décalage à appliquer.                         *
*                off1 = second décalage à appliquer.                          *
*                                                                             *
*  Description : Crée une représentation de fonction virtuelle avec covariant.*
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_override_type_new_with_covariant(GDataType *base, const call_offset_t *off0, const call_offset_t *off1)
{
    GOverrideType *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_OVERRIDE_TYPE, NULL);

    result->base = base;
    result->offsets[0] = *off0;
    result->offsets[1] = *off1;
    result->with_covariant = true;

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

static bool g_override_type_load(GOverrideType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    call_offset_t *offset;                  /* Décalage à traiter          */
    leb128_t value;                         /* Valeur à dépiler            */
    bool status;                            /* Valeur booléenne            */

    result = G_DATA_TYPE_CLASS(g_override_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    type->base = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));
    result = (type->base != NULL);
    if (!result) goto exit;

    for (i = 0; i < 2; i++)
    {
        offset = &type->offsets[i];

        result = unpack_leb128(&value, pbuf);
        if (!result) goto exit;

        offset->values[0] = value;

        result = unpack_leb128(&value, pbuf);
        if (!result) goto exit;

        offset->values[1] = value;

        result = extract_packed_buffer(pbuf, &status, sizeof(uint8_t), false);
        if (!result) goto exit;

        offset->virtual = (status == 0x01);

    }

    result = extract_packed_buffer(pbuf, &status, sizeof(uint8_t), false);
    if (!result) goto exit;

    type->with_covariant = (status == 0x01);

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

static bool g_override_type_store(const GOverrideType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    const call_offset_t *offset;            /* Décalage à traiter          */

    result = G_DATA_TYPE_CLASS(g_override_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->base), pbuf);
    if (!result) goto exit;

    for (i = 0; i < 2; i++)
    {
        offset = &type->offsets[i];

        result = pack_leb128((leb128_t []){ offset->values[0] }, pbuf);
        if (!result) goto exit;

        result = pack_leb128((leb128_t []){ offset->values[1] }, pbuf);
        if (!result) goto exit;

        result = extend_packed_buffer(pbuf, (uint8_t []){ offset->virtual ? 0x01 : 0x00 }, sizeof(uint8_t), false);
        if (!result) goto exit;

    }

    result = extend_packed_buffer(pbuf, (uint8_t []){ type->with_covariant ? 0x01 : 0x00 }, sizeof(uint8_t), false);

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

static guint g_override_type_hash(const GOverrideType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    result = g_data_type_hash(type->base);

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

static GDataType *g_override_type_dup(const GOverrideType *type)
{
    GDataType *result;                      /* Nouvelle instance à renvoyer*/
    GDataType *base;                       /* Copie du type interne       */

    base = g_data_type_dup(type->base);

    if (type->with_covariant)
        result = g_override_type_new_with_covariant(base, &type->offsets[0], &type->offsets[1]);

    else
        result = g_override_type_new(base, &type->offsets[0]);

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

static char *g_override_type_to_string(const GOverrideType *type, bool include)
{
    char *result;                           /* Chaîne finale à renvoyer    */

    result = g_data_type_to_string(type->base, include);
    if (result == NULL) goto exit;

    char *offset_to_string(const call_offset_t *off, char *base)
    {
        char *tmp;                          /* Conversion temporaire       */

        asprintf(&tmp, "%zd", off->values[0]);
        base = stradd(base, tmp);
        free(tmp);

        if (off->virtual)
        {
            base = stradd(base, "_");

            asprintf(&tmp, "%zd", off->values[1]);
            base = stradd(base, tmp);
            free(tmp);

        }

        return base;

    }

    result = offset_to_string(&type->offsets[0], result);

    if (type->with_covariant)
        result = offset_to_string(&type->offsets[0], result);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type de base comportant la fonction virtuelle.    *
*                                                                             *
*  Retour      : Type de base traité.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_override_type_get_base(const GOverrideType *type)
{
    GDataType *result;                      /* Type à retourner            */

    result = type->base;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                off0 = premier décalage à appliquer. [OUT]                   *
*                off1 = second décalage à appliquer.  [OUT]                   *
*                                                                             *
*  Description : Fournit les décalages appliquée pour une fonction virtuelle. *
*                                                                             *
*  Retour      : true si un covariant est pris en compte, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_override_type_get_offsets(const GOverrideType *type, call_offset_t *off0, call_offset_t *off1)
{
    bool result;                        /* Nature à retourner          */

    result = type->with_covariant;

    *off0 = type->offsets[0];
    *off1 = type->offsets[1];

    return result;

}
