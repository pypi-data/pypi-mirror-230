
/* Chrysalide - Outil d'analyse de fichiers binaires
 * template.c - manipulation des types reposant sur des gabarits
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


#include "template.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../type-int.h"
#include "../../common/extstr.h"
#include "../../common/leb128.h"



/* Description de type reposant sur des gabarits (instance) */
struct _GTemplateType
{
    GDataType parent;                       /* A laisser en premier        */

    char *name;                             /* Désignation de la base      */

    GDataType **params;                     /* Sous-types associés         */
    size_t count;                           /* Quantité de ces paramètres  */

};

/* Description de type reposant sur des gabarits (classe) */
struct _GTemplateTypeClass
{
    GDataTypeClass parent;                  /* A laisser en premier        */

};


/* Initialise la classe des types reposant sur des gabarits. */
static void g_template_type_class_init(GTemplateTypeClass *);

/* Initialise l'instance d'un type reposant sur des gabarits. */
static void g_template_type_init(GTemplateType *);

/* Supprime toutes les références externes. */
static void g_template_type_dispose(GTemplateType *);

/* Procède à la libération totale de la mémoire. */
static void g_template_type_finalize(GTemplateType *);

/* Charge un objet depuis une mémoire tampon. */
static bool g_template_type_load(GTemplateType *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool g_template_type_store(const GTemplateType *, GObjectStorage *, packed_buffer_t *);

/* Calcule une empreinte pour un type de données. */
static guint g_template_type_hash(const GTemplateType *);

/* Crée un copie d'un type existant. */
static GDataType *g_template_type_dup(const GTemplateType *);

/* Décrit le type fourni sous forme de caractères. */
static char *g_template_type_to_string(const GTemplateType *, bool);



/* Indique le type défini pour un type reposant sur des gabarits. */
G_DEFINE_TYPE(GTemplateType, g_template_type, G_TYPE_DATA_TYPE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des types reposant sur des gabarits.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_template_type_class_init(GTemplateTypeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDataTypeClass *type;                   /* Version parente et basique  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_template_type_dispose;
    object->finalize = (GObjectFinalizeFunc)g_template_type_finalize;

    type = G_DATA_TYPE_CLASS(klass);

    type->load = (type_load_fc)g_template_type_load;
    type->store = (type_store_fc)g_template_type_store;

    type->hash = (type_hash_fc)g_template_type_hash;
    type->dup = (type_dup_fc)g_template_type_dup;
    type->to_string = (type_to_string_fc)g_template_type_to_string;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise l'instance d'un type reposant sur des gabarits.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_template_type_init(GTemplateType *type)
{
    type->name = NULL;

    type->params = NULL;
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

static void g_template_type_dispose(GTemplateType *type)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < type->count; i++)
        g_clear_object(&type->params[i]);

    G_OBJECT_CLASS(g_template_type_parent_class)->dispose(G_OBJECT(type));

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

static void g_template_type_finalize(GTemplateType *type)
{
    if (type->name != NULL)
        free(type->name);

    if (type->params != NULL)
        free(type->params);

    G_OBJECT_CLASS(g_template_type_parent_class)->finalize(G_OBJECT(type));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une représentation de type reposant sur des gabarits.   *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_template_type_new(void)
{
    GTemplateType *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_TEMPLATE_TYPE, NULL);

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

static bool g_template_type_load(GTemplateType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    size_t i;                               /* Boucle de parcours          */

    result = G_DATA_TYPE_CLASS(g_template_type_parent_class)->load(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->name = calloc(value, sizeof(char));
    result = extract_packed_buffer(pbuf, type->name, value, false);

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    type->count = value;

    type->params = calloc(value, sizeof(GDataType *));

    for (i = 0; i < type->count; i++)
    {
        type->params[i] = G_DATA_TYPE(g_object_storage_unpack_object(storage, "types", pbuf));

        if (type->params[i] == NULL)
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

static bool g_template_type_store(const GTemplateType *type, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t len;                             /* Taille d'une chaîne         */
    size_t i;                               /* Boucle de parcours          */

    result = G_DATA_TYPE_CLASS(g_template_type_parent_class)->store(G_DATA_TYPE(type), storage, pbuf);
    if (!result) goto exit;

    len = strlen(type->name);

    result = pack_uleb128((uleb128_t []){ len }, pbuf);
    if (!result) goto exit;

    result = extend_packed_buffer(pbuf, type->name, len, false);
    if (!result) goto exit;

    result = pack_uleb128((uleb128_t []){ type->count }, pbuf);
    if (!result) goto exit;

    for (i = 0; i < type->count; i++)
    {
        result = g_object_storage_pack_object(storage, "types", G_SERIALIZABLE_OBJECT(type->params[i]), pbuf);
        if (!result) goto exit;
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type base sur des gabarits à modifier.                *
*                                                                             *
*  Description : Indique la désignation principale du type.                   *
*                                                                             *
*  Retour      : Désignation humaine du type.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_template_type_get_name(GTemplateType *type)
{
    char *result;                           /* Désignation à retourner     */

    result = type->name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type base sur des gabarits à modifier.                *
*                name = désignation humaine du type.                          *
*                                                                             *
*  Description : Précise la désignation principale du type.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_template_type_set_name(GTemplateType *type, const char *name)
{
    if (type->name != NULL)
        free(type->name);

    if (name == NULL)
        type->name = NULL;
    else
        type->name = strdup(name);

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

static guint g_template_type_hash(const GTemplateType *type)
{
    guint result;                           /* Empreinte à renvoyer        */
    size_t i;                               /* Boucle de parcours          */

    if (type->name == NULL)
        result = 0;
    else
        result = g_str_hash(type->name);

    for (i = 0; i < type->count; i++)
        result ^= g_data_type_hash(type->params[i]);

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

static GDataType *g_template_type_dup(const GTemplateType *type)
{
    GTemplateType *result;                  /* Copie à retourner           */
    size_t i;                               /* Boucle de parcours          */
    GDataType *param;                       /* Paramètre copié             */

    result = G_TEMPLATE_TYPE(g_template_type_new());

    if (type->name != NULL)
        g_template_type_set_name(result, type->name);

    for (i = 0; i < type->count; i++)
    {
        param = g_data_type_dup(type->params[i]);
        g_template_type_add_param(result, param);
        g_object_unref(G_OBJECT(param));
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

static char *g_template_type_to_string(const GTemplateType *type, bool include)
{
    char *result;                           /* Valeur à renvoyer           */
    size_t i;                               /* Boucle de parcours          */
    char *param;                            /* Paramètre à décrire         */

    if (type->name != NULL)
        result = strdup(type->name);
    else
        result = NULL;

    result = stradd(result, "<");

    for (i = 0; i < type->count; i++)
    {
        if (i > 0) result = stradd(result, ", ");

        param = g_data_type_to_string(type->params[i], include);
        if (param == NULL) goto error;

        result = stradd(result, param);
        free(param);

    }

    result = stradd(result, ">");

    return result;

 error:

    free(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type à mettre à jour.                                *
*                param = nouveau paramètre à intégrer au gabarit.             *
*                                                                             *
*  Description : Ajoute un paramètre à un gabarit.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_template_type_add_param(GTemplateType *type, GDataType *param)
{
    g_object_ref(G_OBJECT(param));

    type->params = realloc(type->params, ++type->count * sizeof(GDataType *));
    type->params[type->count - 1] = param;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique le nombre de paramètres associés au gabarit.         *
*                                                                             *
*  Retour      : Nombre de paramètres inclus dans le gabarit.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_template_type_count_params(const GTemplateType *type)
{
    return type->count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type à consulter.                                    *
*                index = indice du paramètre à retourner.                     *
*                                                                             *
*  Description : Fournit un paramètre donné du gabarit.                       *
*                                                                             *
*  Retour      : Type inclus dans le modèle ou NULL si mauvais indice.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_template_type_get_param(const GTemplateType *type, size_t index)
{
    GDataType *result;                      /* Paramètre à retourner       */

    assert(index < type->count);

    if (index < type->count)
    {
        result = type->params[index];
        g_object_ref(G_OBJECT(result));
    }

    else
        result = NULL;

    return result;

}
