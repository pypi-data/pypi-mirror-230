
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - contexte lié à l'exécution d'un processeur
 *
 * Copyright (C) 2011-2019 Cyrille Bagard
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



/* Taille des blocs d'allocations */
#define DB_ALLOC_SIZE 20


/* Initialise la classe des contextes de processeur. */
static void g_proc_context_class_init(GProcContextClass *);

/* Initialise une instance de contexte de processeur. */
static void g_proc_context_init(GProcContext *);

/* Supprime toutes les références externes. */
static void g_proc_context_dispose(GProcContext *);

/* Procède à la libération totale de la mémoire. */
static void g_proc_context_finalize(GProcContext *);

/* Ajoute une adresse virtuelle comme point de départ de code. */
static void _g_proc_context_push_drop_point(GProcContext *, DisassPriorityLevel, virt_t, va_list);



/* Indique le type défini par la GLib pour le contexte de processeur. */
G_DEFINE_TYPE(GProcContext, g_proc_context, G_TYPE_PRELOAD_INFO);



/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de processeur.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_proc_context_class_init(GProcContextClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_proc_context_dispose;
    object->finalize = (GObjectFinalizeFunc)g_proc_context_finalize;

	klass->push_point = (push_drop_point_fc)_g_proc_context_push_drop_point;

    g_signal_new("drop-point-pushed",
                 G_TYPE_PROC_CONTEXT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GProcContextClass, drop_point_pushed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de contexte de processeur.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_proc_context_init(GProcContext *ctx)
{
    DisassPriorityLevel i;                   /* Boucle de parcours          */

    for (i = 0; i < DPL_COUNT; i++)
    {
        ctx->drop_points[i] = NULL;
        ctx->dp_allocated[i] = 0;
        ctx->dp_count[i] = 0;
    }

    g_mutex_init(&ctx->dp_access);

    ctx->extra_symbols = NULL;
    ctx->esyms_count = 0;
    g_mutex_init(&ctx->es_access);

    g_mutex_init(&ctx->items_mutex);

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

static void g_proc_context_dispose(GProcContext *ctx)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < ctx->items_count; i++)
        g_clear_object(&ctx->items[i]);

    g_mutex_clear(&ctx->items_mutex);

    G_OBJECT_CLASS(g_proc_context_parent_class)->dispose(G_OBJECT(ctx));

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

static void g_proc_context_finalize(GProcContext *ctx)
{
    DisassPriorityLevel i;                   /* Boucle de parcours          */

    for (i = 0; i < DPL_COUNT; i++)
        if (ctx->drop_points[i] != NULL)
            free(ctx->drop_points[i]);

    if (ctx->extra_symbols != NULL)
        free(ctx->extra_symbols);

    if (ctx->items != NULL)
        free(ctx->items);

    G_OBJECT_CLASS(g_proc_context_parent_class)->finalize(G_OBJECT(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx     = contexte de désassemblage à mettre à jour.         *
*                counter = adresse du compteur à modifier.                    *
*                                                                             *
*  Description : Enregistre un compteur pour le décompte des points à traiter.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proc_context_attach_counter(GProcContext *ctx, gint *counter)
{
    ctx->counter = counter;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx   = contexte de désassemblage à compléter.               *
*                level = indication de priorité et d'origine de l'adresse.    *
*                addr  = adresse d'un nouveau point de départ à traiter.      *
*                ap    = éventuelles informations complémentaires.            *
*                                                                             *
*  Description : Ajoute une adresse virtuelle comme point de départ de code.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _g_proc_context_push_drop_point(GProcContext *ctx, DisassPriorityLevel level, virt_t addr, va_list ap)
{
    assert(level < DPL_COUNT);

    if (ctx->dp_count[level] >= ctx->dp_allocated[level])
    {
        ctx->dp_allocated[level] += DP_ALLOC_BLOCK;

        ctx->drop_points[level] = realloc(ctx->drop_points[level], ctx->dp_allocated[level] * sizeof(virt_t));

    }

    ctx->drop_points[level][ctx->dp_count[level]] = addr;

    ctx->dp_count[level]++;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx   = contexte de désassemblage à compléter.               *
*                level = indication de priorité et d'origine de l'adresse.    *
*                addr  = adresse d'un nouveau point de départ à traiter.      *
*                ...   = éventuelles informations complémentaires.            *
*                                                                             *
*  Description : Ajoute une adresse virtuelle comme point de départ de code.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proc_context_push_drop_point(GProcContext *ctx, DisassPriorityLevel level, virt_t addr, ...)
{
    va_list ap;                             /* Arguments complémentaires ? */

    va_start(ap, addr);

    g_mutex_lock(&ctx->dp_access);

    if (ctx->counter != NULL)
        g_atomic_int_inc(ctx->counter);

    G_PROC_CONTEXT_GET_CLASS(ctx)->push_point(ctx, level, addr, ap);

    g_mutex_unlock(&ctx->dp_access);

    g_signal_emit_by_name(ctx, "drop-point-pushed");

    va_end(ap);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx   = contexte de désassemblage à compléter.               *
*                level = degré d'importance de l'adresse retournée. [OUT]     *
*                virt  = adresse d'un point de départ de code à traiter. [OUT]*
*                                                                             *
*  Description : Fournit une adresse virtuelle comme point de départ de code. *
*                                                                             *
*  Retour      : true si une adresse a pu être dépilée, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_proc_context_pop_drop_point(GProcContext *ctx, DisassPriorityLevel *level, virt_t *virt)
{
    bool result;                            /* Bilan d'accès à retourner   */
    DisassPriorityLevel i;                  /* Boucle de parcours          */

    result = false;

    g_mutex_lock(&ctx->dp_access);

    for (i = 0; i < DPL_COUNT && !result; i++)
        if (ctx->dp_count[i] > 0)
        {
            result = true;

            *level = i;
            *virt = ctx->drop_points[i][0];

            if (ctx->dp_count[i] > 1)
                memmove(&ctx->drop_points[i][0], &ctx->drop_points[i][1],
                        (ctx->dp_count[i] - 1) * sizeof(virt_t));

            ctx->dp_count[i]--;

        }

    g_mutex_unlock(&ctx->dp_access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = contexte de désassemblage à compléter.                *
*                addr = adresse d'un nouveau symbole à traiter.               *
*                                                                             *
*  Description : Empile une adresse de nouveau symbole à prendre en compte.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proc_context_push_new_symbol_at(GProcContext *ctx, const vmpa2t *addr)
{
    g_mutex_lock(&ctx->es_access);

    ctx->extra_symbols = realloc(ctx->extra_symbols, ++ctx->esyms_count * sizeof(vmpa2t));

    copy_vmpa(&ctx->extra_symbols[ctx->esyms_count - 1], addr);

    g_mutex_unlock(&ctx->es_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = contexte de désassemblage à compléter.                *
*                addr = adresse d'un nouveau symbole à traiter.               *
*                                                                             *
*  Description : Dépile une adresse de nouveau symbole à prendre en compte.   *
*                                                                             *
*  Retour      : true si un symbole était bien encore en stock, false sinon.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_proc_context_pop_new_symbol_at(GProcContext *ctx, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */

    g_mutex_lock(&ctx->es_access);

    result = (ctx->esyms_count > 0);

    if (result)
    {
        ctx->esyms_count--;
        copy_vmpa(addr, &ctx->extra_symbols[ctx->esyms_count]);
    }

    g_mutex_unlock(&ctx->es_access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = contexte de désassemblage générique à consulter.      *
*                item = élément pour base de données à conserver.             *
*                                                                             *
*  Description : Note la mise en place d'un élément pendant le désassemblage. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proc_context_add_db_item(GProcContext *ctx, GDbItem *item)
{
    g_mutex_lock(&ctx->items_mutex);

    if ((ctx->items_count + 1) > ctx->items_allocated)
    {
        ctx->items_allocated += DB_ALLOC_SIZE;

        ctx->items = realloc(ctx->items, sizeof(GDbItem *) * ctx->items_allocated);

    }

    ctx->items[ctx->items_count++] = item;

    g_mutex_unlock(&ctx->items_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = contexte de désassemblage générique à consulter.      *
*                func = fonction à appeler pour chaque élément.               *
*                data = éventuelles données à associer à l'appel.             *
*                                                                             *
*  Description : Effectue un traitement sur chaque élement de base de données.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_proc_context_foreach_db_item(GProcContext *ctx, GFunc func, void *data)
{
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&ctx->items_mutex);

    for (i = 0; i < ctx->items_count; i++)
        func(ctx->items[i], data);

    g_mutex_unlock(&ctx->items_mutex);

}
