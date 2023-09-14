
/* Chrysalide - Outil d'analyse de fichiers binaires
 * delayed.c - gestion des travaux différés
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "delayed.h"


#include <assert.h>
#include <inttypes.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>


#include "delayed-int.h"
#include "../core/nproc.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../gui/core/global.h"
#endif



/* -------------------------- TACHE DIFFEREE DANS LE TEMPS -------------------------- */


/* Initialise la classe des travaux différés. */
static void g_delayed_work_class_init(GDelayedWorkClass *);

/* Initialise une instance de travail différé. */
static void g_delayed_work_init(GDelayedWork *);

/* Supprime toutes les références externes. */
static void g_delayed_work_dispose(GDelayedWork *);

/* Procède à la libération totale de la mémoire. */
static void g_delayed_work_finalize(GDelayedWork *);

/* Mène l'opération programmée. */
static void g_delayed_work_process(GDelayedWork *, GtkStatusStack *);



/* -------------------------- THREAD DE TRAITEMENTS DEDIES -------------------------- */


#define G_TYPE_WORK_GROUP               g_work_group_get_type()
#define G_WORK_GROUP(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_work_group_get_type(), GWorkGroup))
#define G_IS_WORK_GROUP(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_work_group_get_type()))
#define G_WORK_GROUP_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_WORK_GROUP, GWorkGroupClass))
#define G_IS_WORK_GROUP_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_WORK_GROUP))
#define G_WORK_GROUP_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_WORK_GROUP, GWorkGroupClass))


/* File de traitement pour un type donné (instance) */
typedef struct _GWorkGroup
{
    GObject parent;                         /* A laisser en premier        */

    wgroup_id_t id;                         /* Identifiant de travaux menés*/

    GDelayedWork *works;                    /* Tâches à mener à bien       */
    GMutex mutex;                           /* Verrou pour l'accès         */
    GCond cond;                             /* Réveil pour un traitement   */
    GCond wait_cond;                        /* Réveil d'attente de fin     */
    gint pending;                           /* Tâches en cours d'exécution */

    GThread **threads;                      /* Procédure de traitement     */
    guint threads_count;                    /* Nombre de procédures        */
    bool force_exit;                        /* Procédure d'arrêt           */

    wait_for_incoming_works_cb callback;    /* Encadre les attentes de fin */
    void *data;                             /* Données à associer          */

} GWorkGroup;

/* File de traitement pour un type donné (classe) */
typedef struct _GWorkGroupClass
{
    GObjectClass parent;                    /* A laisser en premier        */

} GWorkGroupClass;


/* Indique le type défini pour les groupes de travail. */
static GType g_work_group_get_type(void);

/* Initialise la classe des groupes de travail. */
static void g_work_group_class_init(GWorkGroupClass *);

/* Initialise une instance de groupe de travail. */
static void g_work_group_init(GWorkGroup *);

/* Supprime toutes les références externes. */
static void g_work_group_dispose(GWorkGroup *);

/* Procède à la libération totale de la mémoire. */
static void g_work_group_finalize(GWorkGroup *);

/* Crée un nouveau thread dédié à un type de travaux donné. */
static GWorkGroup *g_work_group_new(wgroup_id_t, const guint *);

/* Fournit l'identifiant associé à un groupe de travail. */
static wgroup_id_t g_work_group_get_id(const GWorkGroup *);

/* Place une nouvelle tâche en attente dans une file dédiée. */
static void g_work_group_schedule(GWorkGroup *, GDelayedWork *);

/* Assure le traitement en différé. */
static void *g_work_group_process(GWorkGroup *);

/* Détermine si le groupe est vide de toute programmation. */
static bool g_work_group_is_empty(GWorkGroup *);

/* Attend que toutes les tâches d'un groupe soient traitées. */
static void g_work_group_wait_for_completion(GWorkGroup *, GWorkQueue *);

/* Modifie les conditions d'attente des fins d'exécutions. */
static void g_work_group_set_extra_wait_callback(GWorkGroup *, wait_for_incoming_works_cb, void *);

/* Force un réveil d'une attente en cours pour la confirmer. */
static void g_work_group_wake_up_waiters(GWorkGroup *);



/* ------------------------- TRAITEMENT DE TACHES DIFFEREES ------------------------- */


/* Gestionnaire des travaux différés (instance) */
struct _GWorkQueue
{
    GObject parent;                         /* A laisser en premier        */

    wgroup_id_t generator;                  /* Générateur d'identifiants   */

    GWorkGroup **groups;                    /* Files de traitement         */
    size_t groups_count;                    /* Nombre de files internes    */
    GMutex mutex;                           /* Verrou pour l'accès         */
    GCond wait_all;                         /* Réveil d'attente globale    */

};

/* Gestionnaire des travaux différés (classe) */
struct _GWorkQueueClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des travaux différés. */
static void g_work_queue_class_init(GWorkQueueClass *);

/* Initialise une instance de gestionnaire de travaux différés. */
static void g_work_queue_init(GWorkQueue *);

/* Supprime toutes les références externes. */
static void g_work_queue_dispose(GWorkQueue *);

/* Procède à la libération totale de la mémoire. */
static void g_work_queue_finalize(GWorkQueue *);

/* Donne l'assurance de l'existence d'un groupe de travail. */
static bool g_work_queue_ensure_group_exists(GWorkQueue *, wgroup_id_t, const guint *);

/* Fournit le groupe de travail correspondant à un identifiant. */
static GWorkGroup *g_work_queue_find_group_for_id(GWorkQueue *, wgroup_id_t);



/* ---------------------------------------------------------------------------------- */
/*                            TACHE DIFFEREE DANS LE TEMPS                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les travaux différés. */
G_DEFINE_TYPE(GDelayedWork, g_delayed_work, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des travaux différés.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_work_class_init(GDelayedWorkClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_delayed_work_dispose;
    object->finalize = (GObjectFinalizeFunc)g_delayed_work_finalize;

    g_signal_new("work-completed",
                 G_TYPE_DELAYED_WORK,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GDelayedWorkClass, work_completed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de travail différé.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_work_init(GDelayedWork *work)
{
    work->completed = false;
    g_mutex_init(&work->mutex);
    g_cond_init(&work->cond);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_work_dispose(GDelayedWork *work)
{
    g_mutex_clear(&work->mutex);
    g_cond_clear(&work->cond);

    G_OBJECT_CLASS(g_delayed_work_parent_class)->dispose(G_OBJECT(work));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_work_finalize(GDelayedWork *work)
{
    G_OBJECT_CLASS(g_delayed_work_parent_class)->finalize(G_OBJECT(work));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work   = travail à effectuer.                                *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Mène l'opération programmée.                                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_work_process(GDelayedWork *work, GtkStatusStack *status)
{
    G_DELAYED_WORK_GET_CLASS(work)->run(work, status);

    g_mutex_lock(&work->mutex);

    work->completed = true;

    g_cond_signal(&work->cond);
    g_mutex_unlock(&work->mutex);

    g_signal_emit_by_name(work, "work-completed");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = travail à surveiller.                                 *
*                                                                             *
*  Description : Attend la fin de l'exécution d'une tâche donnée.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_delayed_work_wait_for_completion(GDelayedWork *work)
{
    g_mutex_lock(&work->mutex);

    while (!work->completed)
        g_cond_wait(&work->cond, &work->mutex);

    g_mutex_unlock(&work->mutex);

}



/* ---------------------------------------------------------------------------------- */
/*                           THREADS DES TRAITEMENTS DEDIES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les groupes de travail. */
G_DEFINE_TYPE(GWorkGroup, g_work_group, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des groupes de travail.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_class_init(GWorkGroupClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_work_group_dispose;
    object->finalize = (GObjectFinalizeFunc)g_work_group_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de groupe de travail.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_init(GWorkGroup *group)
{
    group->works = NULL;

    g_mutex_init(&group->mutex);
    g_cond_init(&group->cond);
    g_cond_init(&group->wait_cond);

    g_atomic_int_set(&group->pending, 0);

    group->threads = NULL;
    group->threads_count = 0;
    group->force_exit = false;

    group->callback = NULL;
    group->data = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_dispose(GWorkGroup *group)
{
    guint i;                                /* Boucle de parcours          */
    GDelayedWork *work;                     /* Travail à oublier           */

    group->force_exit = true;

    /**
     * Concernant la pose du verrou, se référer aux commentaires de la
     * fonction g_work_group_process().
     */

    g_mutex_lock(&group->mutex);

    g_cond_broadcast(&group->cond);

    g_mutex_unlock(&group->mutex);

    for (i = 0; i < group->threads_count; i++)
        g_thread_join(group->threads[i]);

    while (!dl_list_empty(group->works))
    {
        work = group->works;
        delayed_work_list_del(work, &group->works);

        g_object_unref(G_OBJECT(work));

    }

    g_mutex_clear(&group->mutex);
    g_cond_clear(&group->cond);
    g_cond_clear(&group->wait_cond);

    G_OBJECT_CLASS(g_work_group_parent_class)->dispose(G_OBJECT(group));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_finalize(GWorkGroup *group)
{
    if (group->threads != NULL)
        free(group->threads);

    G_OBJECT_CLASS(g_work_group_parent_class)->finalize(G_OBJECT(group));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id    = identifiant accordé au nouveau groupe.               *
*                count = quantité de threads à allouer.                       *
*                                                                             *
*  Description : Crée un nouveau thread dédié à un type de travaux donné.     *
*                                                                             *
*  Retour      : Structure associée au thread mise en place.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GWorkGroup *g_work_group_new(wgroup_id_t id, const guint *count)
{
    GWorkGroup *result;                    /* Traiteur à retourner        */
    guint i;                                /* Boucle de parcours          */
    char name[16];                          /* Désignation humaine         */

    result = g_object_new(G_TYPE_WORK_GROUP, NULL);

    result->id = id;

    result->threads_count = get_max_online_threads();

    if (count != NULL && *count < result->threads_count)
        result->threads_count = *count;

    result->threads = (GThread **)calloc(result->threads_count, sizeof(GThread *));

    for (i = 0; i < result->threads_count; i++)
    {
        snprintf(name, sizeof(name), "wgrp_%" PRIu64 "-%u", id, i);

        result->threads[i] = g_thread_new(name, (GThreadFunc)g_work_group_process, result);
        if (!result->threads[i])
            goto start_error;

    }

 start_error:

    result->threads_count = i;

    assert(i > 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = gestionnaire des actions à mener.                    *
*                                                                             *
*  Description : Fournit l'identifiant associé à un groupe de travail.        *
*                                                                             *
*  Retour      : Identifiant unique attribué au groupe de travail.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static wgroup_id_t g_work_group_get_id(const GWorkGroup *group)
{
    return group->id;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = gestionnaire des actions à mener.                    *
*                work  = nouvelle tâche à programmer, puis effectuer.         *
*                                                                             *
*  Description : Place une nouvelle tâche en attente dans une file dédiée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_schedule(GWorkGroup *group, GDelayedWork *work)
{
    g_mutex_lock(&group->mutex);

    g_atomic_int_inc(&group->pending);

    delayed_work_list_add_tail(work, &group->works);

    g_cond_signal(&group->cond);

    g_mutex_unlock(&group->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = gestionnaire des actions à mener.                    *
*                                                                             *
*  Description : Assure le traitement en différé.                             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *g_work_group_process(GWorkGroup *group)
{
    GDelayedWork *work;                     /* Traitement à mener          */
    GtkStatusStack *status;                 /* Zone d'info éventuelle      */

    while (1)
    {
        g_mutex_lock(&group->mutex);

        while (dl_list_empty(group->works) && !group->force_exit)
            g_cond_wait(&group->cond, &group->mutex);

        if (group->force_exit)
        {
            g_mutex_unlock(&group->mutex);
            break;
        }

        work = group->works;
        delayed_work_list_del(work, &group->works);

        g_mutex_unlock(&group->mutex);

#ifdef INCLUDE_GTK_SUPPORT
        status = get_global_status();
#else
        status = NULL;
#endif
        g_delayed_work_process(work, status);

        g_object_unref(G_OBJECT(work));

        /**
         * Verrou ou pas verrou ?
         *
         * La documentation de la GLib indique que ce n'est pas nécessaire :
         *
         *    '''
         *    It is good practice to lock the same mutex as the waiting threads
         *    while calling this function, though not required.
         *    '''
         *
         * Ce conseil se trouve verbatim à l'adresse :
         *
         *    https://developer.gnome.org/glib/stable/glib-Threads.html#g-cond-broadcast
         *
         * Dans la pratique, il peut arriver que l'attente de la fonction
         * g_work_group_wait_for_completion() ne soit jamais interrompue.
         *
         * La documentation POSIX est un peu plus orientée :
         *
         *    '''
         *    The pthread_cond_broadcast() functions may be called by a thread
         *    whether or not it currently owns the mutex that threads calling
         *    pthread_cond_wait() have associated with the condition variable
         *    during their waits; however, if predictable scheduling behavior is
         *    required, then that mutex shall be locked by the thread calling
         *    pthread_cond_broadcast().
         *    '''
         *
         * Ce passage complet est consultable à l'adresse :
         *
         *    http://pubs.opengroup.org/onlinepubs/9699919799/functions/pthread_cond_broadcast.html
         *
         * La page de manuel pthread_cond_broadcast(3) est quant à elle plus
         * directrice : aucun complément d'information sur le sujet n'est fourni
         * et les exemples associés utilisent implicement un verrou pendant
         * sont appel.
         */

        g_mutex_lock(&group->mutex);

        if (g_atomic_int_dec_and_test(&group->pending))
            g_cond_broadcast(&group->wait_cond);

        g_mutex_unlock(&group->mutex);

    }

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = gestionnaire des actions à consulter.                *
*                                                                             *
*  Description : Détermine si le groupe est vide de toute programmation.      *
*                                                                             *
*  Retour      : Etat du groupe de travail.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_work_group_is_empty(GWorkGroup *group)
{
    bool result;                            /* Etat à retourner            */

    /**
     * Pour que le résultat soit exploitable, il ne doit pas varier
     * en dehors de la zone couverte par le verrou du groupe avant
     * son utilisation par l'appelant.
     *
     * Il doit donc logiquement y avoir un autre verrou en amont et,
     * comme à priori on ne devrait pas bloquer les groupes principaux
     * pour un traitement particulier, cette procédure ne devrait concerner
     * que des groupes dynamiques.
     */

    g_mutex_lock(&group->mutex);

    result = dl_list_empty(group->works);

    g_mutex_unlock(&group->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = groupe dont les conclusions sont attendues.          *
*                queue = queue d'appartenance pour les appels externes.       *
*                                                                             *
*  Description : Attend que toutes les tâches d'un groupe soient traitées.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_wait_for_completion(GWorkGroup *group, GWorkQueue *queue)
{
    wait_for_incoming_works_cb callback;    /* Procédure complémentaire    */

    bool no_extra_check(GWorkQueue *_q, wgroup_id_t _id, void *_data)
    {
        return false;
    }

    callback = group->callback != NULL ? group->callback : no_extra_check;

    g_mutex_lock(&group->mutex);

    /**
     * On attend que :
     *  - la liste des tâches programmées soit vide.
     *  - il n'existe plus de tâche en cours.
     *  - rien n'indique que de nouvelles tâches supplémentaires vont arriver.
     */

    while ((g_atomic_int_get(&group->pending) > 0 || callback(queue, group->id, group->data))
           && !group->force_exit)
    {
        g_cond_wait(&group->wait_cond, &group->mutex);
    }

    g_mutex_unlock(&group->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group    = groupe dont les paramètres sont à modifier.       *
*                callback = éventuelle fonction à appeler ou NULL.            *
*                data     = données devant accompagner l'appel.               *
*                                                                             *
*  Description : Modifie les conditions d'attente des fins d'exécutions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_set_extra_wait_callback(GWorkGroup *group, wait_for_incoming_works_cb callback, void *data)
{
    group->callback = callback;
    group->data = data;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue    = gestionnaire de l'ensemble des groupes de travail.*
*                id       = identifiant d'un groupe de travail.               *
*                                                                             *
*  Description : Force un réveil d'une attente en cours pour la confirmer.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_group_wake_up_waiters(GWorkGroup *group)
{
    /**
     * Concernant la pose du verrou, se référer aux commentaires de la
     * fonction g_work_group_process().
     */

    g_mutex_lock(&group->mutex);

    g_cond_broadcast(&group->wait_cond);

    g_mutex_unlock(&group->mutex);

}



/* ---------------------------------------------------------------------------------- */
/*                           TRAITEMENT DE TACHES DIFFEREES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour le gestionnaire des travaux différés. */
G_DEFINE_TYPE(GWorkQueue, g_work_queue, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des travaux différés.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_queue_class_init(GWorkQueueClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_work_queue_dispose;
    object->finalize = (GObjectFinalizeFunc)g_work_queue_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de gestionnaire de travaux différés. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_queue_init(GWorkQueue *queue)
{
    queue->generator = 0;

    queue->groups = NULL;
    queue->groups_count = 0;
    g_mutex_init(&queue->mutex);
    g_cond_init(&queue->wait_all);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_queue_dispose(GWorkQueue *queue)
{
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&queue->mutex);

    for (i = 0; i < queue->groups_count; i++)
        g_object_unref(G_OBJECT(queue->groups[i]));

    g_mutex_unlock(&queue->mutex);

    g_mutex_clear(&queue->mutex);
    g_cond_clear(&queue->wait_all);

    G_OBJECT_CLASS(g_work_queue_parent_class)->dispose(G_OBJECT(queue));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_work_queue_finalize(GWorkQueue *queue)
{
    if (queue->groups != NULL)
        free(queue->groups);

    G_OBJECT_CLASS(g_work_queue_parent_class)->finalize(G_OBJECT(queue));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Créé un nouveau gestionnaire de tâches parallèles.           *
*                                                                             *
*  Retour      : Gestionnaire de traitements mis en place.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GWorkQueue *g_work_queue_new(void)
{
    GWorkQueue *result;                     /* Instance à retourner        */

    result = g_object_new(G_TYPE_WORK_QUEUE, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                id    = identifiant d'un groupe de travail.                  *
*                count = quantité de threads à allouer.                       *
*                                                                             *
*  Description : Donne l'assurance de l'existence d'un groupe de travail.     *
*                                                                             *
*  Retour      : true si un nouveau groupe a été constitué, false sinon.      *
*                                                                             *
*  Remarques   : Le verrou d'accès doit être posé par l'appelant.             *
*                                                                             *
******************************************************************************/

static bool g_work_queue_ensure_group_exists(GWorkQueue *queue, wgroup_id_t id, const guint *count)
{
    bool found;                             /* Bilan des recherches        */
    size_t i;                               /* Boucle de parcours          */
    GWorkGroup *group;                      /* Groupe à consulter          */

    assert(!g_mutex_trylock(&queue->mutex));

    found = false;

    for (i = 0; i < queue->groups_count && !found; i++)
    {
        group = queue->groups[i];
        found = (g_work_group_get_id(group) == id);
    }

    if (!found)
    {
        queue->groups_count++;
        queue->groups = (GWorkGroup **)realloc(queue->groups,
                                               queue->groups_count * sizeof(GWorkGroup *));

        group = g_work_group_new(id, count);
        queue->groups[queue->groups_count - 1] = group;

    }

    return !found;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                                                                             *
*  Description : Constitue un nouveau groupe de travail.                      *
*                                                                             *
*  Retour      : Nouvel identifiant unique d'un nouveau groupe de travail.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t g_work_queue_define_work_group(GWorkQueue *queue)
{
    wgroup_id_t result;                     /* Valeur à retourner          */
    bool created;                           /* Bilan d'une tentative       */

    g_mutex_lock(&queue->mutex);

    do
    {
        result = queue->generator++;
        created = g_work_queue_ensure_group_exists(queue, result, NULL);
    }
    while (!created);

    g_mutex_unlock(&queue->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                count = quantité de threads à allouer.                       *
*                                                                             *
*  Description : Constitue un nouveau petit groupe de travail.                *
*                                                                             *
*  Retour      : Nouvel identifiant unique d'un nouveau groupe de travail.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t g_work_queue_define_tiny_work_group(GWorkQueue *queue, guint count)
{
    wgroup_id_t result;                     /* Valeur à retourner          */
    bool created;                           /* Bilan d'une tentative       */

    g_mutex_lock(&queue->mutex);

    do
    {
        result = queue->generator++;
        created = g_work_queue_ensure_group_exists(queue, result, &count);
    }
    while (!created);

    g_mutex_unlock(&queue->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                id    = identifiant d'un groupe de travail.                  *
*                                                                             *
*  Description : Dissout un groupe de travail existant.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_work_queue_delete_work_group(GWorkQueue *queue, wgroup_id_t id)
{
    size_t i;                               /* Boucle de parcours          */
    GWorkGroup *group;                      /* Groupe de travail manipulé  */
#ifndef NDEBUG
    bool found;                             /* Repérage du groupe visé     */
#endif

#ifndef NDEBUG
    found = false;
#endif

    g_mutex_lock(&queue->mutex);

    for (i = 0; i < queue->groups_count; i++)
    {
        group = queue->groups[i];

        if (g_work_group_get_id(group) == id)
        {
            g_object_unref(G_OBJECT(group));

            memmove(&queue->groups[i], &queue->groups[i + 1],
                    (queue->groups_count - i - 1) * sizeof(GWorkGroup *));

            queue->groups_count--;
            queue->groups = (GWorkGroup **)realloc(queue->groups,
                                                   queue->groups_count * sizeof(GWorkGroup *));

#ifndef NDEBUG
            found = true;
#endif

            break;

        }

    }

    assert(found);

    g_cond_broadcast(&queue->wait_all);

    g_mutex_unlock(&queue->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire des actions à mener.                    *
*                work  = nouvelle tâche à programmer, puis effectuer.         *
*                id    = identifiant du groupe de travail d'affectation.      *
*                                                                             *
*  Description : Place une nouvelle tâche en attente.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_work_queue_schedule_work(GWorkQueue *queue, GDelayedWork *work, wgroup_id_t id)
{
    GWorkGroup *group;                      /* Groupe de travail à attendre*/

    group = g_work_queue_find_group_for_id(queue, id);
    assert(group != NULL);

    g_work_group_schedule(group, work);

    g_object_unref(G_OBJECT(group));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                id    = identifiant d'un groupe de travail.                  *
*                                                                             *
*  Description : Fournit le groupe de travail correspondant à un identifiant. *
*                                                                             *
*  Retour      : Eventuel groupe existant trouvé ou NULL si aucun.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GWorkGroup *g_work_queue_find_group_for_id(GWorkQueue *queue, wgroup_id_t id)
{
    GWorkGroup *result;                     /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    g_mutex_lock(&queue->mutex);

    for (i = 0; i < queue->groups_count; i++)
        if (g_work_group_get_id(queue->groups[i]) == id)
        {
            result = queue->groups[i];
            g_object_ref(G_OBJECT(result));
            break;
        }

    g_mutex_unlock(&queue->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                id    = identifiant d'un groupe de travail.                  *
*                                                                             *
*  Description : Détermine si un groupe est vide de toute programmation.      *
*                                                                             *
*  Retour      : Etat du groupe de travail.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_work_queue_is_empty(GWorkQueue *queue, wgroup_id_t id)
{
    bool result;                            /* Etat à retourner            */
    GWorkGroup *group;                      /* Groupe de travail à attendre*/

    group = g_work_queue_find_group_for_id(queue, id);

    if (group != NULL)
    {
        result = g_work_group_is_empty(group);
        g_object_unref(G_OBJECT(group));
    }

    else
        result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                id    = identifiant d'un groupe de travail.                  *
*                                                                             *
*  Description : Attend que toutes les tâches d'un groupe soient traitées.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_work_queue_wait_for_completion(GWorkQueue *queue, wgroup_id_t id)
{
    GWorkGroup *group;                      /* Groupe de travail à attendre*/

    group = g_work_queue_find_group_for_id(queue, id);

    if (group != NULL)
    {
        g_work_group_wait_for_completion(group, queue);
        g_object_unref(G_OBJECT(group));
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue    = gestionnaire de l'ensemble des groupes de travail.*
*                gb_ids   = identifiants de groupes globaux.                  *
*                gb_count = nombre de ces groupes globaux.                    *
*                                                                             *
*  Description : Attend que toutes les tâches de tout groupe soient traitées. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_work_queue_wait_for_all_completions(GWorkQueue *queue, const wgroup_id_t *gb_ids, size_t gb_count)
{
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&queue->mutex);

 wait_again:

    /**
     * Attente d'éventuels groupes isolés.
     */

    while (queue->groups_count > gb_count)
        g_cond_wait(&queue->wait_all, &queue->mutex);

    g_mutex_unlock(&queue->mutex);

    /**
     * Attente des groupes principaux.
     */

    for (i = 0; i < gb_count; i++)
        g_work_queue_wait_for_completion(queue, gb_ids[i]);

    /**
     * Si le groupe par défaut a généré de nouveaux groupes, on recommence !
     */

    g_mutex_lock(&queue->mutex);

    if (queue->groups_count > gb_count)
        goto wait_again;

    g_mutex_unlock(&queue->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue    = gestionnaire de l'ensemble des groupes de travail.*
*                id       = identifiant d'un groupe de travail.               *
*                callback = éventuelle fonction à appeler ou NULL.            *
*                data     = données devant accompagner l'appel.               *
*                                                                             *
*  Description : Modifie les conditions d'attente des fins d'exécutions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_work_queue_set_extra_wait_callback(GWorkQueue *queue, wgroup_id_t id, wait_for_incoming_works_cb callback, void *data)
{
    GWorkGroup *group;                      /* Groupe de travail à traiter */

    group = g_work_queue_find_group_for_id(queue, id);

    if (group != NULL)
    {
        g_work_group_set_extra_wait_callback(group, callback, data);
        g_object_unref(G_OBJECT(group));
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue    = gestionnaire de l'ensemble des groupes de travail.*
*                id       = identifiant d'un groupe de travail.               *
*                                                                             *
*  Description : Force un réveil d'une attente en cours pour la confirmer.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_work_queue_wake_up_waiters(GWorkQueue *queue, wgroup_id_t id)
{
    GWorkGroup *group;                      /* Groupe de travail à traiter */

    group = g_work_queue_find_group_for_id(queue, id);

    if (group != NULL)
    {
        g_work_group_wake_up_waiters(group);
        g_object_unref(G_OBJECT(group));
    }

}
