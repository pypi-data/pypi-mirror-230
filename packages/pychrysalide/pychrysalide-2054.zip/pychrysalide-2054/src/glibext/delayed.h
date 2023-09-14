
/* Chrysalide - Outil d'analyse de fichiers binaires
 * delayed.h - prototypes pour la gestion des travaux différés
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


#ifndef _GLIBEXT_DELAYED_H
#define _GLIBEXT_DELAYED_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>



/* -------------------------- TACHE DIFFEREE DANS LE TEMPS -------------------------- */


#define G_TYPE_DELAYED_WORK               g_delayed_work_get_type()
#define G_DELAYED_WORK(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_delayed_work_get_type(), GDelayedWork))
#define G_IS_DELAYED_WORK(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_delayed_work_get_type()))
#define G_DELAYED_WORK_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DELAYED_WORK, GDelayedWorkClass))
#define G_IS_DELAYED_WORK_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DELAYED_WORK))
#define G_DELAYED_WORK_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DELAYED_WORK, GDelayedWorkClass))


/* Travail différé (instance) */
typedef struct _GDelayedWork GDelayedWork;

/* Travail différé (classe) */
typedef struct _GDelayedWorkClass GDelayedWorkClass;


/* Indique le type défini pour les travaux différés. */
GType g_delayed_work_get_type(void);

/* Attend la fin de l'exécution d'une tâche donnée. */
void g_delayed_work_wait_for_completion(GDelayedWork *);



/* ------------------------- TRAITEMENT DE TACHES DIFFEREES ------------------------- */


#define G_TYPE_WORK_QUEUE               g_work_queue_get_type()
#define G_WORK_QUEUE(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_work_queue_get_type(), GWorkQueue))
#define G_IS_WORK_QUEUE(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_work_queue_get_type()))
#define G_WORK_QUEUE_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_WORK_QUEUE, GWorkQueueClass))
#define G_IS_WORK_QUEUE_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_WORK_QUEUE))
#define G_WORK_QUEUE_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_WORK_QUEUE, GWorkQueueClass))


/* Gestionnaire des travaux différés (instance) */
typedef struct _GWorkQueue GWorkQueue;

/* Gestionnaire des travaux différés (classe) */
typedef struct _GWorkQueueClass GWorkQueueClass;


/**
 * Identifiant unique pour groupe de travail.
 *
 * Le nombre de bits est forcé à 64 bits car glib-genmarshal ne reconnait
 * pas explicitement le type 'unsigned long long'.
 */
typedef uint64_t wgroup_id_t;


/* Indique le type défini pour le gestionnaire des travaux différés. */
GType g_work_queue_get_type(void);

/* Créé un nouveau gestionnaire de tâches parallèles. */
GWorkQueue *g_work_queue_new(void);

/* Constitue un nouveau groupe de travail. */
wgroup_id_t g_work_queue_define_work_group(GWorkQueue *);

/* Constitue un nouveau petit groupe de travail. */
wgroup_id_t g_work_queue_define_tiny_work_group(GWorkQueue *, guint);

/* Dissout un groupe de travail existant. */
void g_work_queue_delete_work_group(GWorkQueue *, wgroup_id_t);

/* Place une nouvelle tâche en attente. */
void g_work_queue_schedule_work(GWorkQueue *, GDelayedWork *, wgroup_id_t);

/* Détermine si un groupe est vide de toute programmation. */
bool g_work_queue_is_empty(GWorkQueue *, wgroup_id_t);

/* Attend que toutes les tâches d'un groupe soient traitées. */
void g_work_queue_wait_for_completion(GWorkQueue *, wgroup_id_t);

/* Attend que toutes les tâches de tout groupe soient traitées. */
void g_work_queue_wait_for_all_completions(GWorkQueue *, const wgroup_id_t *, size_t);


/* Etudie le besoin d'attendre d'avantage de prochaines tâches. */
typedef bool (* wait_for_incoming_works_cb) (GWorkQueue *, wgroup_id_t, void *);


/* Modifie les conditions d'attente des fins d'exécutions. */
void g_work_queue_set_extra_wait_callback(GWorkQueue *, wgroup_id_t, wait_for_incoming_works_cb, void *);

/* Force un réveil d'une attente en cours pour la confirmer. */
void g_work_queue_wake_up_waiters(GWorkQueue *, wgroup_id_t);



#endif  /* _GLIBEXT_DELAYED_H */
