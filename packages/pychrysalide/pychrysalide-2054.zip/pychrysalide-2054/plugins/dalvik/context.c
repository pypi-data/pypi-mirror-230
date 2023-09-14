
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - contexte lié à l'exécution d'un processeur
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "context.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <analysis/contents/restricted.h>
#include <arch/context-int.h>
#include <arch/instructions/raw.h>
#include <common/sort.h>
#include <plugins/dex/dex-int.h>


#include "operands/register.h"



/* ------------------------ MANIPULATION GLOBALE DU CONTEXTE ------------------------ */


/* Mémorisation de données brutes dans le code */
typedef struct _raw_data_area
{
    mrange_t range;                         /* Couverture à laisser en 1er */

    phys_t item_len;                        /* Taille de chaque élément    */

    bool padding;                           /* Constitution d'un bourrage ?*/

} raw_data_area;

/* Définition d'un contexte pour processeur Dalkvik (instance) */
struct _GDalvikContext
{
    GProcContext parent;                    /* A laisser en premier        */

    raw_data_area *data;                    /* Liste de zones brutes       */
    size_t count;                           /* Taille de cette liste       */
    GMutex mutex;                           /* Accès à la liste            */

};


/* Définition d'un contexte pour processeur Dalkvik (classe) */
struct _GDalvikContextClass
{
    GProcContextClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des contextes de processeur Dalkvik. */
static void g_dalvik_context_class_init(GDalvikContextClass *);

/* Initialise une instance de contexte de processeur Dalkvik. */
static void g_dalvik_context_init(GDalvikContext *);

/* Supprime toutes les références externes. */
static void g_dalvik_context_dispose(GDalvikContext *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_context_finalize(GDalvikContext *);



/* ---------------------------------------------------------------------------------- */
/*                          MANIPULATION GLOBALE DU CONTEXTE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour le contexte de processeur Dalkvik. */
G_DEFINE_TYPE(GDalvikContext, g_dalvik_context, G_TYPE_PROC_CONTEXT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de processeur Dalkvik.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_context_class_init(GDalvikContextClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_context_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_context_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de contexte de processeur Dalkvik.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_context_init(GDalvikContext *ctx)
{
    g_mutex_init(&ctx->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_context_dispose(GDalvikContext *ctx)
{
    g_mutex_clear(&ctx->mutex);

    G_OBJECT_CLASS(g_dalvik_context_parent_class)->dispose(G_OBJECT(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_context_finalize(GDalvikContext *ctx)
{
    if (ctx->data != NULL)
        free(ctx->data);

    G_OBJECT_CLASS(g_dalvik_context_parent_class)->finalize(G_OBJECT(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un contexte pour l'exécution du processeur Dalvik.      *
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDalvikContext *g_dalvik_context_new(void)
{
    GDalvikContext *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_DALVIK_CONTEXT, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx    = contexte de désassemblage Dalvik à actualiser.      *
*                start  = début de la zone à considérer.                      *
*                length = taille de la zone couverte.                         *
*                                                                             *
*  Description : Mémorise une zone comme étant des données de branchements.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dalvik_context_register_switch_data(GDalvikContext *ctx, const vmpa2t *start, phys_t length)
{
    bool result;                            /* Bilan à retourner           */
    raw_data_area new;                      /* Nouvel élément à insérer    */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    g_mutex_lock(&ctx->mutex);

    /* Vérification quant aux chevauchements */

    init_mrange(&new.range, start, length);

    for (i = 0; i < ctx->count && result; i++)
        result = !mrange_intersects_mrange(&ctx->data[i].range, &new.range);

    /* Insertion d'une nouvelle zone */

    if (result)
    {
        new.item_len = 4;
        new.padding = false;

        ctx->data = qinsert(ctx->data, &ctx->count, sizeof(raw_data_area),
                            (__compar_fn_t)cmp_mrange_with_vmpa_swapped, &new);

    }

    g_mutex_unlock(&ctx->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx    = contexte de désassemblage Dalvik à actualiser.      *
*                start  = début de la zone à considérer.                      *
*                width  = taille de chacun des éléments.                      *
*                length = taille de la zone couverte.                         *
*                                                                             *
*  Description : Mémorise une zone comme étant des données d'un tableau.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dalvik_context_register_array_data(GDalvikContext *ctx, const vmpa2t *start, uint16_t width, phys_t length)
{
    bool result;                            /* Bilan à retourner           */
    raw_data_area new;                      /* Nouvel élément à insérer    */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    g_mutex_lock(&ctx->mutex);

    /* Vérification quant aux chevauchements */

    init_mrange(&new.range, start, length);

    for (i = 0; i < ctx->count && result; i++)
        result = !mrange_intersects_mrange(&ctx->data[i].range, &new.range);

    /* Insertion d'une nouvelle zone */

    if (result)
    {
        assert(length % width == 0);

        new.item_len = width;
        new.padding = false;

        ctx->data = qinsert(ctx->data, &ctx->count, sizeof(raw_data_area),
                            (__compar_fn_t)cmp_mrange_with_vmpa_swapped, &new);

    }

    g_mutex_unlock(&ctx->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx    = contexte de désassemblage Dalvik à actualiser.      *
*                start  = début de la zone à considérer.                      *
*                                                                             *
*  Description : Mémorise une zone comme étant un bourrage de fin de tableau. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_dalvik_context_register_array_data_padding(GDalvikContext *ctx, const vmpa2t *start)
{
    bool result;                            /* Bilan à retourner           */
    raw_data_area new;                      /* Nouvel élément à insérer    */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    g_mutex_lock(&ctx->mutex);

    /* Vérification quant aux chevauchements */

    init_mrange(&new.range, start, sizeof(uint8_t));

    for (i = 0; i < ctx->count && result; i++)
        result = !mrange_intersects_mrange(&ctx->data[i].range, &new.range);

    /* Insertion d'une nouvelle zone */

    if (result)
    {
        new.item_len = sizeof(uint8_t);
        new.padding = true;

        ctx->data = qinsert(ctx->data, &ctx->count, sizeof(raw_data_area),
                            (__compar_fn_t)cmp_mrange_with_vmpa_swapped, &new);

    }

    g_mutex_unlock(&ctx->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx     = contexte de désassemblage Dalvik à consulter.      *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                                                                             *
*  Description : Place une donnée en tant qu'instruction si besoin est.       *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_dalvik_context_get_raw_data(GDalvikContext *ctx, const GBinContent *content, vmpa2t *pos)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    raw_data_area *found;                   /* Zone de couverture trouvée  */
    GBinContent *restricted;                /* Zone de lecture effective   */
    phys_t length;                          /* Zone de couverture          */
    size_t count;                           /* Nombre d'éléments           */

    result = NULL;

    g_mutex_lock(&ctx->mutex);

    found = bsearch(pos, ctx->data, ctx->count, sizeof(raw_data_area),
                    (__compar_fn_t)cmp_mrange_with_vmpa_swapped);

    if (found)
    {
        restricted = g_restricted_content_new_ro(content, &found->range);

        length = get_mrange_length(&found->range);
        count = length / found->item_len;

        switch (found->item_len)
        {
            case 1:
                result = g_raw_instruction_new_array(restricted, MDS_8_BITS_UNSIGNED, count, pos, SRE_LITTLE);
                break;

            case 2:
                result = g_raw_instruction_new_array(restricted, MDS_16_BITS_UNSIGNED, count, pos, SRE_LITTLE);
                break;

            case 4:
                result = g_raw_instruction_new_array(restricted, MDS_32_BITS_UNSIGNED, count, pos, SRE_LITTLE);
                break;

            case 8:
                result = g_raw_instruction_new_array(restricted, MDS_64_BITS_UNSIGNED, count, pos, SRE_LITTLE);
                break;

            default:
                result = g_raw_instruction_new_array(restricted, MDS_8_BITS_UNSIGNED,
                                                     length, pos, SRE_LITTLE);
                break;

        }

        if (result != NULL && found->padding)
            g_raw_instruction_mark_as_padding(G_RAW_INSTRUCTION(result), true);

        g_object_unref(G_OBJECT(restricted));

    }

    g_mutex_unlock(&ctx->mutex);

    return result;

}
