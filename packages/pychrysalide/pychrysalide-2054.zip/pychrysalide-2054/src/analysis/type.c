
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.h - prototypes pour la manipulation des types en tout genre
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "type.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "type-int.h"
#include "storage/serialize.h"
#include "../common/extstr.h"
#include "../common/leb128.h"



/* Initialise la classe des types quelconques. */
static void g_data_type_class_init(GDataTypeClass *);

/* Initialise l'instance d'un type quelconque. */
static void g_data_type_init(GDataType *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_serializable_object_interface_init(GSerializableObjectIface *);

/* Supprime toutes les références externes. */
static void g_data_type_dispose(GDataType *);

/* Procède à la libération totale de la mémoire. */
static void g_data_type_finalize(GDataType *);

/* Charge un objet depuis une mémoire tampon. */
static bool _g_data_type_load(GDataType *, GObjectStorage *, packed_buffer_t *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_data_type_load(GDataType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool _g_data_type_store(const GDataType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_data_type_store(const GDataType *, GObjectStorage *, packed_buffer_t *);



/* Indique le type défini pour un type quelconque. */
G_DEFINE_TYPE_WITH_CODE(GDataType, g_data_type, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_serializable_object_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types quelconques.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_data_type_class_init(GDataTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_data_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_data_type_finalize;

    klass->load = (type_load_fc)_g_data_type_load;
    klass->store = (type_store_fc)_g_data_type_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type quelconque.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_data_type_init(GDataType *type)
{
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    INIT_GOBJECT_EXTRA_LOCK(extra);

    g_data_type_set_qualifiers(type, TQF_NONE);

    type->namespace = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de sérialisation.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_serializable_object_interface_init(GSerializableObjectIface *iface)
{
    iface->load = (load_serializable_object_cb)g_data_type_load;
    iface->store = (store_serializable_object_cb)g_data_type_store;

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

static void g_data_type_dispose(GDataType *type)
{
    g_clear_object(&type->namespace);

    G_OBJECT_CLASS(g_data_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_data_type_finalize(GDataType *type)
{
    G_OBJECT_CLASS(g_data_type_parent_class)->finalize(G_OBJECT(type));

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

static bool _g_data_type_load(GDataType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    char ns_sep[2];                         /* Séparateur d'éléments       */
    GDataType *namespace;                   /* Espace de noms / classe     */

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    g_data_type_set_qualifiers(type, value);

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    g_data_type_set_flags(type, value);

    result = extract_packed_buffer(pbuf, ns_sep, 2 * sizeof(char), false);
    if (!result) goto exit;

    if (ns_sep[0] != '\0')
    {
        namespace = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));

        result = (namespace != NULL);
        if (!result) goto exit;

        result = g_data_type_set_namespace(type, namespace, ns_sep);
        assert(result);

        g_object_unref(G_OBJECT(namespace));

    }

 exit:

    return result;

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

static bool g_data_type_load(GDataType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GDataTypeClass *class;                  /* Classe du type              */

    class = G_DATA_TYPE_GET_CLASS(type);

    result = class->load(type, storage, pbuf);

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

static bool _g_data_type_store(const GDataType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    type_extra_data_t *extra;               /* Données insérées à modifier */

    result = pack_uleb128((uleb128_t []){ g_data_type_get_qualifiers(type) }, pbuf);
    if (!result) goto exit;

    result = pack_uleb128((uleb128_t []){ g_data_type_get_flags(type) }, pbuf);
    if (!result) goto exit;

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    result = extend_packed_buffer(pbuf, extra->ns_sep, 2 * sizeof(char), false);
    if (!result) goto unlocking_exit;

    if (extra->ns_sep[0] != '\0')
    {
        assert(type->namespace != NULL);

        result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->namespace), pbuf);
        if (!result) goto unlocking_exit;

    }

 unlocking_exit:

    UNLOCK_GOBJECT_EXTRA(extra);

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

static bool g_data_type_store(const GDataType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GDataTypeClass *class;                  /* Classe du type              */

    class = G_DATA_TYPE_GET_CLASS(type);

    result = class->store(type, storage, pbuf);

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

guint g_data_type_hash(const GDataType *type)
{
    guint result;                           /* Empreinte à renvoyer        */
    GDataTypeClass *class;                  /* Classe du type              */

    class = G_DATA_TYPE_GET_CLASS(type);

    result = class->hash(type);

    result ^= g_int_hash((gint []){ g_data_type_get_qualifiers(type) });

    if (type->namespace != NULL)
        result ^= g_data_type_hash(type->namespace);

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

GDataType *g_data_type_dup(const GDataType *type)
{
    GDataType *result;                      /* Copie à retourner           */
    GDataTypeClass *class;                  /* Classe du type              */
    type_extra_data_t *extra;               /* Données insérées à modifier */
    GDataType *ns;                          /* Eventuel espace de noms     */
    bool status;                            /* Bilan d'un rattachement     */

    class = G_DATA_TYPE_GET_CLASS(type);

    result = class->dup(type);

    g_data_type_set_qualifiers(result, g_data_type_get_qualifiers(type));

    g_data_type_set_flags(result, g_data_type_get_flags(type));

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    if (extra->ns_sep[0] != '\0')
    {
        assert(type->namespace != NULL);

        ns = g_data_type_dup(type->namespace);

        status = g_data_type_set_namespace(result, ns, extra->ns_sep);
        assert(status);

        g_object_unref(G_OBJECT(ns));

        if (!status)
            g_clear_object(&result);

    }

    UNLOCK_GOBJECT_EXTRA(extra);

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

char *g_data_type_to_string(const GDataType *type, bool include)
{
    char *result;                           /* Chaîne à retourner          */
    GDataTypeClass *class;                  /* Classe du type              */
    type_extra_data_t *extra;               /* Données insérées à modifier */
    char *namespace;                        /* Groupe d'appartenance       */
    TypeQualifier qualifiers;               /* Qualificatifs du type       */

    class = G_DATA_TYPE_GET_CLASS(type);

    result = class->to_string(type, include);

    if (result == NULL)
        result = strdup("");

    if (include)
    {
        extra = GET_DATA_TYPE_EXTRA(type);

        LOCK_GOBJECT_EXTRA(extra);

        if (type->namespace != NULL && g_data_type_handle_namespaces(type))
        {
            namespace = g_data_type_to_string(type->namespace, true);

            result = strprep(result, extra->ns_sep);
            result = strprep(result, namespace);

            free(namespace);

        }

        UNLOCK_GOBJECT_EXTRA(extra);

    }

    qualifiers = g_data_type_get_qualifiers(type);

    if (qualifiers & TQF_RESTRICT)
        result = strprep(result, "restrict ");

    if (qualifiers & TQF_VOLATILE)
        result = strprep(result, "volatile ");

    if (qualifiers & TQF_CONST)
        result = strprep(result, "const ");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type       = instance à mettre à jour.                       *
*                qualifiers = nouveaux qualificatifs pour le type.            *
*                                                                             *
*  Description : Définit l'ensemble des qualificatifs d'une instance de type. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_data_type_set_qualifiers(GDataType *type, TypeQualifier qualifiers)
{
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    extra->qualifiers = qualifiers;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type      = instance à mettre à jour.                        *
*                qualifier = nouveau qualificatif pour le type.               *
*                                                                             *
*  Description : Ajoute un qualificatif à une instance de type.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_data_type_add_qualifier(GDataType *type, TypeQualifier qualifier)
{
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    extra->qualifiers |= qualifier;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit les qualificatifs associés à une instance de type.   *
*                                                                             *
*  Retour      : Qualificatifs éventuels.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

TypeQualifier g_data_type_get_qualifiers(const GDataType *type)
{
    TypeQualifier result;                   /* Qualificatifs à renvoyer    */
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->qualifiers;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type      = type à mettre à jour.                            *
*                namespace = instance d'appartenance.                         *
*                sep       = séparateur à utiliser entre les éléments.        *
*                                                                             *
*  Description : Définit le groupe d'appartenance d'un type donné.            *
*                                                                             *
*  Retour      : true si la définition est effective, false en cas de rejet.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_data_type_set_namespace(GDataType *type, GDataType *namespace, const char *sep)
{
    bool result;                            /* Bilan à retourner           */
    type_extra_data_t *extra;               /* Données insérées à modifier */

    result = ((namespace == NULL && sep == NULL) || (namespace != NULL && sep != NULL && sep[0] != '\0'));

    if (result)
    {
        extra = GET_DATA_TYPE_EXTRA(type);

        LOCK_GOBJECT_EXTRA(extra);

        if (sep == NULL)
        {
            extra->ns_sep[0] = '\0';
            extra->ns_sep[1] = '\0';
        }
        else
        {
            extra->ns_sep[0] = sep[0];
            extra->ns_sep[1] = sep[1];
        }

        if (type->namespace != NULL)
            g_object_unref(G_OBJECT(type->namespace));

        type->namespace = namespace;

        g_object_ref(G_OBJECT(namespace));

        UNLOCK_GOBJECT_EXTRA(extra);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit le groupe d'appartenance d'un type donné.            *
*                                                                             *
*  Retour      : Eventuelle instance d'appartenance ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_data_type_get_namespace(const GDataType *type)
{
    GDataType *result;                      /* Espace à renvoyer           */
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    result = type->namespace;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Fournit la chaîne de séparation entre deux entités.          *
*                                                                             *
*  Retour      : Eventuelle chaîne de séparation ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_data_type_get_namespace_separator(const GDataType *type)
{
    char *result;                           /* Séparateur à retourner      */
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    if (extra->ns_sep[0] == '\0')
        result = NULL;

    else if (extra->ns_sep[1] == '\0')
        result = strndup(extra->ns_sep, 1);

    else
        result = strndup(extra->ns_sep, 2);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

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

bool g_data_type_handle_namespaces(const GDataType *type)
{
    bool result;                            /* Bilan à retourner           */
    GDataTypeClass *class;                  /* Classe du type              */

    class = G_DATA_TYPE_GET_CLASS(type);

    if (class->handle_ns != NULL)
        result = class->handle_ns(type);
    else
        result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type       = instance à mettre à jour.                       *
*                flags = nouvelles propriétés pour le type.                   *
*                                                                             *
*  Description : Définit l'ensemble des fanions d'une instance de type.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_data_type_set_flags(GDataType *type, TypeFlag flags)
{
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    extra->flags = flags;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type      = instance à mettre à jour.                        *
*                flag = nouvelle propriété pour le type.                      *
*                                                                             *
*  Description : Ajoute un fanion à une instance de type.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_data_type_add_flag(GDataType *type, TypeFlag flag)
{
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    extra->flags |= flag;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit les fanions associés à une instance de type.         *
*                                                                             *
*  Retour      : Qualificatifs éventuels.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

TypeFlag g_data_type_get_flags(const GDataType *type)
{
    TypeFlag result;                        /* Propriétés à renvoyer       */
    type_extra_data_t *extra;               /* Données insérées à modifier */

    extra = GET_DATA_TYPE_EXTRA(type);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->flags;

    UNLOCK_GOBJECT_EXTRA(extra);

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

bool g_data_type_is_pointer(const GDataType *type)
{
    bool result;                            /* Bilan à retourner           */
    GDataTypeClass *class;                  /* Classe du type              */

    class = G_DATA_TYPE_GET_CLASS(type);

    if (class->is_pointer != NULL)
        result = class->is_pointer(type);
    else
        result = false;

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

bool g_data_type_is_reference(const GDataType *type)
{
    bool result;                            /* Bilan à retourner           */
    GDataTypeClass *class;                  /* Classe du type              */

    class = G_DATA_TYPE_GET_CLASS(type);

    if (class->is_reference != NULL)
        result = class->is_reference(type);
    else
        result = false;

    return result;

}
