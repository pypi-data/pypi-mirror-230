
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.c - données associées à un flux de données Kaitai
 *
 * Copyright (C) 2023 Cyrille Bagard
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
#include <limits.h>
#include <malloc.h>
#include <string.h>


#include "array-int.h"
#include "expression.h"



/* Initialise la classe des flux de données pour Kaitai. */
static void g_kaitai_array_class_init(GKaitaiArrayClass *);

/* Initialise un flux de données accessibles à Kaitai. */
static void g_kaitai_array_init(GKaitaiArray *);

/* Supprime toutes les références externes. */
static void g_kaitai_array_dispose(GKaitaiArray *);

/* Procède à la libération totale de la mémoire. */
static void g_kaitai_array_finalize(GKaitaiArray *);

/* Détermine la taille de la séquence d'octets du tableau. */
static bool g_kaitai_array_compute_bytes_length(const GKaitaiArray *, size_t *);



/* Indique le type défini pour un tableau rassemblant des éléments Kaitai. */
G_DEFINE_TYPE(GKaitaiArray, g_kaitai_array, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tableau d'éléments Kaitai.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_array_class_init(GKaitaiArrayClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_kaitai_array_dispose;
    object->finalize = (GObjectFinalizeFunc)g_kaitai_array_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise un tableau rassemblant des éléments divers.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_array_init(GKaitaiArray *array)
{
    array->items = NULL;
    array->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_array_dispose(GKaitaiArray *array)
{
    G_OBJECT_CLASS(g_kaitai_array_parent_class)->dispose(G_OBJECT(array));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_kaitai_array_finalize(GKaitaiArray *array)
{
    G_OBJECT_CLASS(g_kaitai_array_parent_class)->finalize(G_OBJECT(array));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue une amorce de tableau pour rassembler des éléments.*
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiArray *g_kaitai_array_new(void)
{
    GKaitaiArray *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_KAITAI_ARRAY, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau Kaitai à consulter.                          *
*                                                                             *
*  Description : Dénombre le nombre d'éléments enregistrés.                   *
*                                                                             *
*  Retour      : Taille du tableau manipulé.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_kaitai_array_count_items(const GKaitaiArray *array)
{
    size_t result;                          /* Quantité à retourner        */

    result = array->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau Kaitai à compléter.                          *
*                item  = élément Kaitai à archiver.                           *
*                                                                             *
*  Description : Intègre un élément supplémentaire dans un tableau Kaitai.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_kaitai_array_append_item(GKaitaiArray *array, const resolved_value_t *item)
{
    array->items = realloc(array->items, ++array->count * sizeof(resolved_value_t));

    COPY_RESOLVED_VALUE(array->items[array->count - 1], *item);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = ensemble de correspondances attribut/binaire.        *
*                index = indice de la correspondance visée.                   *
*                item  = élément archivé dans le talbeau à fournir. [OUT]     *
*                                                                             *
*  Description : Fournit un élément ciblé dans un tableau Kaitai.             *
*                                                                             *
*  Retour      : Validité de l'emplacmeent pour élément à renseigner.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_array_get_item(const GKaitaiArray *array, size_t index, resolved_value_t *item)
{
    bool result;                            /* Bilan à retourner           */

    result = (index < array->count);

    if (result)
        COPY_RESOLVED_VALUE(*item, array->items[index]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array  = tableau Kaitai à consulter.                         *
*                length = nombre d'octets représentés. [OUT]                  *
*                                                                             *
*  Description : Détermine la taille de la séquence d'octets du tableau.      *
*                                                                             *
*  Retour      : true si le tableau peut être converti en octets, ou false.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_kaitai_array_compute_bytes_length(const GKaitaiArray *array, size_t *length)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    const resolved_value_t *item;           /* Elément en cours d'analyse  */
    size_t extra;                           /* Taille d'un sous-tableau    */

    result = true;

    *length = 0;

    for (i = 0; i < array->count && result; i++)
    {
        item = &array->items[i];

        switch (item->type)
        {
            case GVT_UNSIGNED_INTEGER:
                result = (item->unsigned_integer <= UCHAR_MAX);
                if (result) (*length)++;
                break;

            case GVT_SIGNED_INTEGER:
                result = (0 <= item->signed_integer && item->signed_integer <= SCHAR_MAX);
                if (result) (*length)++;
                break;

            case GVT_BYTES:
                *length += item->bytes.len;
                break;

            case GVT_ARRAY:
                result = g_kaitai_array_compute_bytes_length(item->array, &extra);
                if (result) *length += extra;
                break;

            default:
                result = false;
                break;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau Kaitai à consulter.                          *
*                bytes = conversion en série d'octets équivalent. [OUT]       *
*                                                                             *
*  Description : Convertit un tableau d'éléments en séquence d'octets.        *
*                                                                             *
*  Retour      : true si une série d'octets a pu être constituée, ou false.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_kaitai_array_convert_to_bytes(const GKaitaiArray *array, sized_string_t *bytes)
{
    bool result;                            /* Bilan à retourner           */
    size_t length;                          /* Taille de la chaîne finale  */
    size_t i;                               /* Boucle de parcours          */
    const resolved_value_t *item;           /* Elément en cours d'analyse  */
    char *iter;                             /* Tête d'écriture             */
    sized_string_t extra;                   /* Données d'un sous-tableau   */

    /* Détermination de la taille finale */

    result = g_kaitai_array_compute_bytes_length(array, &length);

    /* Construction d'une chaîne d'octets si possible */

    if (result)
    {
        bytes->data = malloc(length * sizeof(char));
        bytes->len = length;

        iter = bytes->data;

        for (i = 0; i < array->count; i++)
        {
            item = &array->items[i];

            switch (item->type)
            {
                case GVT_UNSIGNED_INTEGER:
                    *iter = item->unsigned_integer;
                    iter++;
                    break;

                case GVT_SIGNED_INTEGER:
                    *iter = item->signed_integer;
                    iter++;
                    break;

                case GVT_BYTES:
                    memcpy(iter, item->bytes.data, item->bytes.len);
                    iter += item->bytes.len;
                    break;

                case GVT_ARRAY:
                    result = g_kaitai_array_convert_to_bytes(item->array, &extra);
                    assert(result);

                    memcpy(iter, extra.data, extra.len);
                    iter += extra.len;

                    exit_szstr(&extra);
                    break;

                default:
                    break;

            }

        }

    }

    return result;

}
