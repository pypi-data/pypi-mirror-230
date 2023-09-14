
/* Chrysalide - Outil d'analyse de fichiers binaires
 * literal.c - manipulation des valeurs littérales de types instanciés
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


#include "literal.h"


#include <malloc.h>
#include <stdio.h>
#include <string.h>


#include "basic.h"
#include "../type-int.h"



/* Description de type instancié avec une valeur litérale (instance) */
struct _GLiteralType
{
    GDataType parent;                       /* A laisser en premier        */

    GDataType *orig;                        /* Type instancié              */
    literal_value value;                    /* Valeur d'instance           */

};

/* Description de type instancié avec une valeur litérale (classe) */
struct _GLiteralTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des types instanciés avec des valeurs. */
static void g_literal_type_class_init(GLiteralTypeClass *);

/* Initialise l'instance d'un type instancié avec une valeur. */
static void g_literal_type_init(GLiteralType *);

/* Supprime toutes les références externes. */
static void g_literal_type_dispose(GLiteralType *);

/* Procède à la libération totale de la mémoire. */
static void g_literal_type_finalize(GLiteralType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_literal_type_load(GLiteralType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_literal_type_store(const GLiteralType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_literal_type_hash(const GLiteralType *);

/* Crée un copie d'un type existant. */
static GDataType *g_literal_type_dup(const GLiteralType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_literal_type_to_string(const GLiteralType *, bool);



/* Indique le type défini pour un type reposant sur des gabarits. */
G_DEFINE_TYPE(GLiteralType, g_literal_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types instanciés avec des valeurs.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_literal_type_class_init(GLiteralTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_literal_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_literal_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_literal_type_load;
    type->store = (type_store_fc)g_literal_type_store;

    type->hash = (type_hash_fc)g_literal_type_hash;
    type->dup = (type_dup_fc)g_literal_type_dup;
    type->to_string = (type_to_string_fc)g_literal_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type instancié avec une valeur.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_literal_type_init(GLiteralType *type)
{
    type->orig = NULL;

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

static void g_literal_type_dispose(GLiteralType *type)
{
    g_clear_object(&type->orig);

    G_OBJECT_CLASS(g_literal_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_literal_type_finalize(GLiteralType *type)
{
    G_OBJECT_CLASS(g_literal_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : orig  = type d'origine instancié.                            *
*                value = valeur de l'instanciation.                           *
*                                                                             *
*  Description : Crée une représentation de type instancié avec une valeur.   *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_literal_type_new(GDataType *orig, const literal_value *value)
{
    GLiteralType *result;                   /* Structure à retourner       */

    if (!G_IS_BASIC_TYPE(orig))
        result = NULL;

    else
    {
        result = g_object_new(G_TYPE_LITERAL_TYPE, NULL);

        result->orig = orig;
        result->value = *value;

    }

    return (result != NULL ? G_DATA_TYPE(result) : NULL);

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

static bool g_literal_type_load(GLiteralType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DATA_TYPE_CLASS(g_literal_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    type->orig = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));
    result = (type->orig != NULL);
    if (!result) goto exit;

    if (g_basic_type_get_base(G_BASIC_TYPE(type->orig)) == BTP_FLOAT)
        result = extract_packed_buffer(pbuf, (uint64_t *)&type->value.float_val, sizeof(uint64_t), true);
    else
        result = extract_packed_buffer(pbuf, (uint32_t *)&type->value.int_val, sizeof(uint32_t), true);

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

static bool g_literal_type_store(const GLiteralType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DATA_TYPE_CLASS(g_literal_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->orig), pbuf);
    if (!result) goto exit;

    if (g_basic_type_get_base(G_BASIC_TYPE(type->orig)) == BTP_FLOAT)
        result = extend_packed_buffer(pbuf, (uint64_t []){ type->value.float_val }, sizeof(uint64_t), true);
    else
        result = extend_packed_buffer(pbuf, (uint32_t []){ type->value.int_val }, sizeof(uint32_t), true);

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

static guint g_literal_type_hash(const GLiteralType *type)
{
    guint result;                           /* Empreinte à renvoyer        */

    result = g_data_type_hash(type->orig);

    if (g_basic_type_get_base(G_BASIC_TYPE(type->orig)) == BTP_FLOAT)
        result ^= g_double_hash((gdouble []){ type->value.float_val });
    else
        result ^= g_int_hash((gint []){ type->value.int_val });

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

static GDataType *g_literal_type_dup(const GLiteralType *type)
{
    GDataType *result;                      /* Copie à retourner           */
    GDataType *orig;                        /* Copie du type interne       */

    orig = g_data_type_dup(type->orig);

    result = g_literal_type_new(orig, &type->value);

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

static char *g_literal_type_to_string(const GLiteralType *type, bool include)
{
    char *result;                           /* Valeur à renvoyer           */

    switch (g_basic_type_get_base(G_BASIC_TYPE(type->orig)))
    {
        case BTP_BOOL:
            result = strdup(type->value.int_val ? "true" : "false");
            break;

        case BTP_INT:
        default:
            asprintf(&result, "%d", type->value.int_val);
            break;

        case BTP_FLOAT:
            asprintf(&result, "%f", type->value.float_val);
            break;

    }

    return result;

}
