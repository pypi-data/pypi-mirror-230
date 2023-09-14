
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - contexte lié à l'exécution d'un processeur
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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
#include <string.h>


#include "context-int.h"



/* ------------------------ MANIPULATION GLOBALE DU CONTEXTE ------------------------ */


/* Initialise la classe des contextes de processeur ARM. */
static void g_arm_context_class_init(GArmContextClass *);

/* Initialise une instance de contexte de processeur ARM. */
static void g_arm_context_init(GArmContext *);

/* Supprime toutes les références externes. */
static void g_arm_context_dispose(GArmContext *);

/* Procède à la libération totale de la mémoire. */
static void g_arm_context_finalize(GArmContext *);

/* Indique l'encodage (générique) utilisé à une adresse donnée. */
static size_t find_disass_arm_area(disass_arm_area *, virt_t, size_t, size_t);



/* ---------------------------------------------------------------------------------- */
/*                          MANIPULATION GLOBALE DU CONTEXTE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour le contexte de processeur ARM. */
G_DEFINE_TYPE(GArmContext, g_arm_context, G_TYPE_PROC_CONTEXT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de processeur ARM.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_context_class_init(GArmContextClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_arm_context_dispose;
    object->finalize = (GObjectFinalizeFunc)g_arm_context_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de contexte de processeur ARM.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_context_init(GArmContext *ctx)
{
    g_mutex_init(&ctx->areas_access);

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

static void g_arm_context_dispose(GArmContext *ctx)
{
    g_mutex_clear(&ctx->areas_access);

    G_OBJECT_CLASS(g_arm_context_parent_class)->dispose(G_OBJECT(ctx));

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

static void g_arm_context_finalize(GArmContext *ctx)
{
    if (ctx->areas != NULL)
        free(ctx->areas);

    G_OBJECT_CLASS(g_arm_context_parent_class)->finalize(G_OBJECT(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un contexte pour l'exécution du processeur ARM.         *
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArmContext *g_arm_context_new(void)
{
    GArmContext *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARM_CONTEXT, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : areas = ensemble des découpages du désassemblage.            *
*                addr = adresse d'un nouveau point de départ à retrouver.     *
*                first = indice de la première zone à considérer.             *
*                last  = indice de la dernière zone à considérer.             *
*                                                                             *
*  Description : Indique l'encodage (générique) utilisé à une adresse donnée. *
*                                                                             *
*  Retour      : Marqueur à priori toujours valide.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t find_disass_arm_area(disass_arm_area *areas, virt_t addr, size_t first, size_t last)
{
    size_t index;                           /* Indice de cellule idéale    */
    size_t mid;                             /* Division de l'espace        */

    if (first == last)
        index = first;

    else
    {
        mid = first + (last - first + 1) / 2;

        if (areas[mid].start <= addr)
            index = find_disass_arm_area(areas, addr, mid, last);
        else
            index = find_disass_arm_area(areas, addr, first, mid - 1);

    }

    assert(areas[index].start <= addr && addr <= areas[index].end);

    return index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx    = contexte de désassemblage à compléter.              *
*                addr   = adresse d'un nouveau point de départ à créer.       *
*                marker = forme générique d'un encodage à mémoriser.          *
*                                                                             *
*  Description : Enregistre l'encodage (générique) utilisé à une adresse.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _g_arm_context_define_encoding(GArmContext *ctx, virt_t addr, unsigned int marker)
{
    size_t selected;                        /* Zone associée à une adresse */

    g_mutex_lock(&ctx->areas_access);

    selected = find_disass_arm_area(ctx->areas, addr, 0, ctx->acount - 1);

    //assert(ctx->areas[selected].start != addr || ctx->areas[selected].marker == marker);

    /* S'agit-il d'une redéfinition ? */
    if (ctx->areas[selected].start == addr)
        ctx->areas[selected].marker = marker;

    /* Sinon on redivise... */
    else
    {
        ctx->areas = realloc(ctx->areas, ++ctx->acount * sizeof(disass_arm_area));

        memmove(&ctx->areas[selected + 1], &ctx->areas[selected],
                (ctx->acount - selected - 1) * sizeof(disass_arm_area));

        ctx->areas[selected].start = ctx->areas[selected + 1].start;
        ctx->areas[selected].end = addr - 1;
        ctx->areas[selected].marker = ctx->areas[selected + 1].marker;

        ctx->areas[selected + 1].start = addr;
        ctx->areas[selected + 1].marker = marker;

    }

    g_mutex_unlock(&ctx->areas_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = contexte de désassemblage à consulter.                *
*                addr = adresse d'un nouveau point de départ à retrouver.     *
*                                                                             *
*  Description : Indique l'encodage (générique) utilisé à une adresse donnée. *
*                                                                             *
*  Retour      : Marqueur à priori toujours valide.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int _g_arm_context_find_encoding(GArmContext *ctx, virt_t addr)
{
    unsigned int result;                    /* Identifiant à retourner     */
    size_t selected;                        /* Zone associée à une adresse */

    g_mutex_lock(&ctx->areas_access);

    selected = find_disass_arm_area(ctx->areas, addr, 0, ctx->acount - 1);

    result = ctx->areas[selected].marker;

    g_mutex_unlock(&ctx->areas_access);

    return result;

}
