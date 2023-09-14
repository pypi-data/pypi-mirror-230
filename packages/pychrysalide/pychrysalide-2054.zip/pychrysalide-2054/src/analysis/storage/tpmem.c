
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tpmem.c - mémorisation des types d'objets mis en cache
 *
 * Copyright (C) 2020 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "tpmem.h"


#include <assert.h>
#include <stdint.h>


#include "../db/misc/rlestr.h"
#include "../../arch/operands/target.h"
#include "../../core/logs.h"



/* Conservation d'une référence sur un type */
typedef struct _gtype_ref_info_t
{
    GType gtype;                            /* Type pour la GLib           */
    gpointer gclass;                        /* Lien vers sa classe         */

    /**
     * La GLib n'est pas très claire sur la taille de GType :
     *
     *    #if     GLIB_SIZEOF_SIZE_T != GLIB_SIZEOF_LONG || !defined __cplusplus
     *    typedef gsize                           GType;
     *    #else   // for historic reasons, C++ links against gulong GTypes
     *    typedef gulong                          GType;
     *    #endif
     *
     * Et :
     *
     *    typedef unsigned $glib_size_type_define gsize;
     *
     * On prend donc le parti de conserver ces types sous forme de valeurs 64 bits
     * lors des enregistrements.
     */

} gtype_ref_info_t;

/* Définition d'une mémoire de types d'objets (instance) */
struct _GTypeMemory
{
    GObject parent;                         /* A laisser en premier        */

    gtype_ref_info_t *gtypes;               /* Types des objets reconnus   */
    size_t count;                           /* Quantité de ces objets      */
    GMutex mutex;                           /* Contrôle d'accès à la liste */

};

/* Définition d'une mémoire de types d'objets (classe) */
struct _GTypeMemoryClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des mémoires de types d'objets. */
static void g_type_memory_class_init(GTypeMemoryClass *);

/* Initialise une instance de mémoire de types d'objets. */
static void g_type_memory_init(GTypeMemory *);

/* Supprime toutes les références externes. */
static void g_type_memory_dispose(GTypeMemory *);

/* Procède à la libération totale de la mémoire. */
static void g_type_memory_finalize(GTypeMemory *);



/* Indique le type défini pour une mémoire de types d'objets. */
G_DEFINE_TYPE(GTypeMemory, g_type_memory, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des mémoires de types d'objets.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_type_memory_class_init(GTypeMemoryClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_type_memory_dispose;
    object->finalize = (GObjectFinalizeFunc)g_type_memory_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de mémoire de types d'objets.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_type_memory_init(GTypeMemory *tpmem)
{
    tpmem->gtypes = NULL;
    tpmem->count = 0;
    g_mutex_init(&tpmem->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_type_memory_dispose(GTypeMemory *tpmem)
{
    uint64_t i;                             /* Boucle de parcours          */

    g_mutex_lock(&tpmem->mutex);

    for (i = 0; i < tpmem->count; i++)
        if (tpmem->gtypes[i].gclass != NULL)
            g_type_class_unref(tpmem->gtypes[i].gclass);

    g_mutex_unlock(&tpmem->mutex);

    g_mutex_clear(&tpmem->mutex);

    G_OBJECT_CLASS(g_type_memory_parent_class)->dispose(G_OBJECT(tpmem));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_type_memory_finalize(GTypeMemory *tpmem)
{
    if (tpmem->gtypes != NULL)
        free(tpmem->gtypes);

    G_OBJECT_CLASS(g_type_memory_parent_class)->finalize(G_OBJECT(tpmem));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une mémoire pour types d'objets.                        *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GTypeMemory *g_type_memory_new(void)
{
    GTypeMemory *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_TYPE_MEMORY, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = mémoire à compléter.                                 *
*                pbuf  = zone tampon à lire.                                  *
*                                                                             *
*  Description : Apprend tous les types mémorisés dans un tampon.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_type_memory_load_types(GTypeMemory *tpmem, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à enregistrer         */
    uleb128_t count;                        /* Nombre d'éléments détectés  */
    uleb128_t i;                            /* Boucle de parcours          */
    rle_string str;                         /* Chaîne à charger            */

    result = unpack_uleb128(&count, pbuf);

    if (result)
    {
        g_mutex_lock(&tpmem->mutex);

        tpmem->count = count;

        assert(tpmem->gtypes == NULL);
        tpmem->gtypes = calloc(count, sizeof(gtype_ref_info_t));

        setup_empty_rle_string(&str);

        for (i = 0; i < tpmem->count && result; i++)
        {
            result = unpack_rle_string(&str, pbuf);
            if (!result) break;

            if (get_rle_string(&str) == NULL)
            {
                exit_rle_string(&str);
                break;
            }

            tpmem->gtypes[i].gtype = g_type_from_name(get_rle_string(&str));
            result = (tpmem->gtypes[i].gtype != 0);

            if (!result)
                log_variadic_message(LMT_ERROR, "Unknown type: '%s'", get_rle_string(&str));

            else
                tpmem->gtypes[i].gclass = g_type_class_ref(tpmem->gtypes[i].gtype);

            exit_rle_string(&str);

        }

    }

    g_mutex_unlock(&tpmem->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = mémoire à manipuler.                                 *
*                pbuf  = zone tampon à venir lire.                            *
*                                                                             *
*  Description : Crée une nouvelle instance d'objet à partir de son type.     *
*                                                                             *
*  Retour      : Instance issue de l'opération ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *g_type_memory_create_object(GTypeMemory *tpmem, packed_buffer_t *pbuf)
{
    GObject *result;                        /* Nouvelle instance à renvoyer*/
    uleb128_t index;                        /* Indice du point d'insertion */
    bool status;                            /* Bilan d'une récupération    */

    result = NULL;

    status = unpack_uleb128(&index, pbuf);

    if (status)
    {
        g_mutex_lock(&tpmem->mutex);

        if (index < tpmem->count)
            result = g_object_new(tpmem->gtypes[index].gtype, NULL);

        g_mutex_unlock(&tpmem->mutex);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = mémoire à manipuler.                                 *
*                obj   = instance dont le type est à mémoriser.               *
*                pbuf  = zone tampon à remplir. [OUT]                         *
*                                                                             *
*  Description : Sauvegarde le type d'un objet instancié.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_type_memory_store_object_gtype(GTypeMemory *tpmem, GObject *obj, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType gtype;                            /* Type à enregistrer          */
    size_t index;                           /* Indice du point d'insertion */

    gtype = G_TYPE_FROM_INSTANCE(obj);

    /**
     * Pour quelques explications sur l'esquive suivante, se rapporter aux
     * commentaires de g_target_operand_unserialize().
     *
     * Dans la situation présente, on ne doit pas enregistrer le type dans le tampon,
     * car l'opérande va relancer l'opération entière (avec un opérande temporaire),
     * ce qui conduirait à l'enregistrement de deux types successifs dans les données.
     */

    if (gtype == G_TYPE_TARGET_OPERAND)
        result = true;

    else
    {
        g_mutex_lock(&tpmem->mutex);

        for (index = 0; index < tpmem->count; index++)
            if (tpmem->gtypes[index].gtype == gtype)
                break;

        if (index == tpmem->count)
        {
            tpmem->gtypes = realloc(tpmem->gtypes, ++tpmem->count * sizeof(gtype_ref_info_t));

            assert(tpmem->count > 0);

            tpmem->gtypes[index].gtype = gtype;
            tpmem->gtypes[index].gclass = g_type_class_ref(gtype);

        }

        g_mutex_unlock(&tpmem->mutex);

        result = pack_uleb128((uleb128_t []){ index }, pbuf);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tpmem = mémoire à consulter.                                 *
*                pbuf  = zone tampon à remplir. [OUT]                         *
*                                                                             *
*  Description : Enregistre tous les types mémorisés dans un tampon.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_type_memory_store_types(GTypeMemory *tpmem, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à enregistrer         */
    uint64_t i;                             /* Boucle de parcours          */
    const gchar *name;                      /* Désignation d'un type       */
    rle_string str;                         /* Chaîne à conserver          */

    g_mutex_lock(&tpmem->mutex);

    result = pack_uleb128((uleb128_t []){ tpmem->count }, pbuf);

    for (i = 0; i < tpmem->count && result; i++)
    {
        name = g_type_name(tpmem->gtypes[i].gtype);

        init_static_rle_string(&str, name);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    g_mutex_unlock(&tpmem->mutex);

    return result;

}
