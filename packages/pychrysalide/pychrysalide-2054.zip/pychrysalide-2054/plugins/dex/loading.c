
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.c - chargements parallèles des éléments de la table globale du format Dex
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


#include "loading.h"


#include <i18n.h>
#include <core/logs.h>
#include <glibext/delayed-int.h>


#include "pool.h"



/* Fraction de routines à limiter (instance) */
struct _GDexLoading
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GObject *target;                        /* Cible à faire évoluer       */

    dex_loading_cb callback;                /* Routine de traitement finale*/
    uint32_t begin;                         /* Point de départ du parcours */
    uint32_t end;                           /* Point d'arrivée exclu       */

    activity_id_t id;                       /* Identifiant pour messages   */

    bool *status;                           /* Bilan global constitué      */

};

/* Fraction de routines à limiter (classe) */
struct _GDexLoadingClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches des chargements pour DEX. */
static void g_dex_loading_class_init(GDexLoadingClass *);

/* Initialise une tâche de chargements pour DEX. */
static void g_dex_loading_init(GDexLoading *);

/* Supprime toutes les références externes. */
static void g_dex_loading_dispose(GDexLoading *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_loading_finalize(GDexLoading *);

/* Assure le chargement pour un format DEX en différé. */
static void g_dex_loading_process(GDexLoading *, GtkStatusStack *);



/* Indique le type défini pour les tâches de chargements pour format DEX. */
G_DEFINE_TYPE(GDexLoading, g_dex_loading, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches des chargements pour DEX.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_loading_class_init(GDexLoadingClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_loading_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_loading_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_dex_loading_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une tâche de chargements pour DEX.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_loading_init(GDexLoading *loading)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_loading_dispose(GDexLoading *loading)
{
    G_OBJECT_CLASS(g_dex_loading_parent_class)->dispose(G_OBJECT(loading));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_loading_finalize(GDexLoading *loading)
{
    G_OBJECT_CLASS(g_dex_loading_parent_class)->finalize(G_OBJECT(loading));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target   = cible finale de l'évolution programmée.           *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                callback = routine de traitements particuliers.              *
*                status   = bilan final à constituer. [OUT]                   *
*                                                                             *
*  Description : Crée une tâche de chargement pour DEX différée.              *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexLoading *g_dex_loading_new(GObject *target, uint32_t begin, uint32_t end, activity_id_t id, dex_loading_cb callback, bool *status)
{
    GDexLoading *result;                    /* Tâche à retourner           */

    result = g_object_new(G_TYPE_DEX_LOADING, NULL);

    result->target = target;

    result->callback = callback;
    result->begin = begin;
    result->end = end;

    result->id = id;

    result->status = status;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study  = étude de routines à mener.                          *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure le chargement pour un format DEX en différé.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_loading_process(GDexLoading *loading, GtkStatusStack *status)
{
    uint32_t i;                             /* Boucle de parcours          */
    GObject *obj;                           /* Object chargé en mémoire    */

    for (i = loading->begin; i < loading->end && *(loading->status); i++)
    {
        obj = loading->callback(loading->target, i);

        if (obj != NULL)
            g_object_unref(obj);

        else
        {
            *(loading->status) = false;
            log_variadic_message(LMT_ERROR, _("Error while loading Dex pool item #%u!"), i);
        }

        gtk_status_stack_update_activity_value(status, loading->id, 1);

    }

}
