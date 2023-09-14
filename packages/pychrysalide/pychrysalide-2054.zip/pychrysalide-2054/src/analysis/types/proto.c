
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proto.c - manipulation des prototypes
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


#include "proto.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/extstr.h"
#include "../../common/leb128.h"



/* Description de prototype (instance) */
struct _GProtoType
{
    GDataType parent;                       /* A laisser en premier        */

    GDataType *ret_type;                    /* Type retourné               */

    GDataType **args;                       /* Sous-types associés         */
    size_t count;                           /* Quantité de ces arguments   */

};

/* Description de prototype (classe) */
struct _GProtoTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des prototypes. */
static void g_proto_type_class_init(GProtoTypeClass *);

/* Initialise l'instance d'un prototype. */
static void g_proto_type_init(GProtoType *);

/* Supprime toutes les références externes. */
static void g_proto_type_dispose(GProtoType *);

/* Procède à la libération totale de la mémoire. */
static void g_proto_type_finalize(GProtoType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_proto_type_load(GProtoType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_proto_type_store(const GProtoType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_proto_type_hash(const GProtoType *);

/* Crée un copie d'un type existant. */
static GDataType *g_proto_type_dup(const GProtoType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_proto_type_to_string(const GProtoType *, bool);

/* Indique si le type assure une gestion des espaces de noms. */
static bool g_proto_type_handle_namespaces(GProtoType *);



/* Indique le type défini pour un prototype. */
G_DEFINE_TYPE(GProtoType, g_proto_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des prototypes.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_proto_type_class_init(GProtoTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_proto_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_proto_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_proto_type_load;
    type->store = (type_store_fc)g_proto_type_store;

    type->hash = (type_hash_fc)g_proto_type_hash;
    type->dup = (type_dup_fc)g_proto_type_dup;
    type->to_string = (type_to_string_fc)g_proto_type_to_string;

    type->handle_ns = (type_handle_ns_fc)g_proto_type_handle_namespaces;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un prototype.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_proto_type_init(GProtoType *type)
{
    type->ret_type = NULL;

    type->args = NULL;
    type->count = 0;

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

static void g_proto_type_dispose(GProtoType *type)
{
    size_t i;                               /* Boucle de parcours          */

    g_clear_object(&type->ret_type);

    for (i = 0; i < type->count; i++)
        g_clear_object(&type->args[i]);

    G_OBJECT_CLASS(g_proto_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_proto_type_finalize(GProtoType *type)
{
    if (type->args != NULL)
        free(type->args);

    G_OBJECT_CLASS(g_proto_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une représentation de prototype.                        *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_proto_type_new(void)
{
    GProtoType *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_PROTO_TYPE, NULL);

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

static bool g_proto_type_load(GProtoType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    size_t i;                               /* Boucle de parcours          */

    result = G_DATA_TYPE_CLASS(g_proto_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    type->ret_type = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));
    result = (type->ret_type != NULL);
    if (!result) goto exit;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->count = value;

    type->args = calloc(value, sizeof(GDataType *));

    for (i = 0; i < type->count; i++)
    {
        type->args[i] = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));

        if (type->args[i] == NULL)
            break;

    }

    result = (i == type->count);

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

static bool g_proto_type_store(const GProtoType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = G_DATA_TYPE_CLASS(g_proto_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->ret_type), pbuf);
    if (!result) goto exit;

    result = pack_uleb128((uleb128_t []){ type->count }, pbuf);
    if (!result) goto exit;

    for (i = 0; i < type->count; i++)
    {
        result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->args[i]), pbuf);
        if (!result) goto exit;
    }

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

static guint g_proto_type_hash(const GProtoType *type)
{
    guint result;                           /* Empreinte à renvoyer        */
    size_t i;                               /* Boucle de parcours          */

    if (type->ret_type == NULL)
        result = 0;
    else
        result = g_data_type_hash(type->ret_type);

    for (i = 0; i < type->count; i++)
        result ^= g_data_type_hash(type->args[i]);

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

static GDataType *g_proto_type_dup(const GProtoType *type)
{
    GProtoType *result;                     /* Copie à retourner           */
    GDataType *ret_type;                    /* Type de retour              */
    size_t i;                               /* Boucle de parcours          */
    GDataType *arg;                         /* Argument copié              */

    result = G_PROTO_TYPE(g_proto_type_new());

    if (type->ret_type != NULL)
    {
        ret_type = g_data_type_dup(type->ret_type);
        g_proto_type_set_return_type(result, ret_type);
        g_object_unref(G_OBJECT(ret_type));
    }

    for (i = 0; i < type->count; i++)
    {
        arg = g_data_type_dup(type->args[i]);
        g_proto_type_add_arg(result, arg);
        g_object_unref(G_OBJECT(arg));
    }

    return G_DATA_TYPE(result);

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

static char *g_proto_type_to_string(const GProtoType *type, bool include)
{
    char *result;                           /* Valeur à renvoyer           */
    GDataType *base;                        /* Version d'instance parente  */
    type_extra_data_t *extra;               /* Données insérées à modifier */
    char *namespace;                        /* Groupe d'appartenance       */
    size_t i;                               /* Boucle de parcours          */
    char *arg;                              /* Argument à décrire          */

    if (type->ret_type != NULL)
    {
        result = g_data_type_to_string(type->ret_type, include);
        if (result == NULL) goto exit;

        result = stradd(result, " ");

    }
    else
        result = NULL;

    result = stradd(result, "(");

    base = G_DATA_TYPE(type);

    if (include)
    {
        extra = GET_DATA_TYPE_EXTRA(base);

        LOCK_GOBJECT_EXTRA(extra);

        if (base->namespace != NULL)
        {
            namespace = g_data_type_to_string(base->namespace, true);
            if (namespace == NULL) goto error;

            result = strprep(result, extra->ns_sep);
            result = strprep(result, namespace);

            free(namespace);

        }

        UNLOCK_GOBJECT_EXTRA(extra);

    }

    result = stradd(result, "*) (");

    for (i = 0; i < type->count; i++)
    {
        if (i > 0) result = stradd(result, ", ");

        arg = g_data_type_to_string(type->args[i], include);
        if (arg == NULL) goto error;

        result = stradd(result, arg);
        free(arg);

    }

    result = stradd(result, ")");

 exit:

    return result;

 error:

    free(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si le type assure une gestion des espaces de noms.   *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_proto_type_handle_namespaces(GProtoType *type)
{
    bool result;                            /* Bilan à retourner           */

    result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à mettre à jour.                                 *
*                ret  = indication sur le type de retour.                     *
*                                                                             *
*  Description : Définit le type de retour d'un prototype.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proto_type_set_return_type(GProtoType *type, GDataType *ret)
{
    if (type->ret_type != NULL)
        g_object_unref(G_OBJECT(type->ret_type));

    if (ret == NULL)
        type->ret_type = NULL;

    else
    {
        g_object_ref(G_OBJECT(ret));
        type->ret_type = ret;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le type de retour d'un prototype.                    *
*                                                                             *
*  Retour      : Indication sur le type de retour en place.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_proto_type_get_return_type(const GProtoType *type)
{
    GDataType *result;                      /* Type de retour à renvoyer   */

    result = type->ret_type;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à mettre à jour.                                 *
*                arg  = nouvel argument à intégrer au prototype.              *
*                                                                             *
*  Description : Ajoute un argument à un prototype.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proto_type_add_arg(GProtoType *type, GDataType *arg)
{
    g_object_ref(G_OBJECT(arg));

    type->args = realloc(type->args, ++type->count * sizeof(GDataType *));
    type->args[type->count - 1] = arg;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique le nombre d'arguments associés au prototype.         *
*                                                                             *
*  Retour      : Nombre de paramètres inclus dans le gabarit.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_proto_type_count_args(const GProtoType *type)
{
    return type->count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type à consulter.                                    *
*                index = indice du type d'argument à retourner.               *
*                                                                             *
*  Description : Fournit un argument donné du prototype.                      *
*                                                                             *
*  Retour      : Type d'argument ou NULL si mauvais indice.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_proto_type_get_arg(const GProtoType *type, size_t index)
{
    GDataType *result;                      /* Argument à retourner        */

    assert(index < type->count);

    if (index < type->count)
    {
        result = type->args[index];
        g_object_ref(G_OBJECT(result));
    }

    else
        result = NULL;

    return result;

}
