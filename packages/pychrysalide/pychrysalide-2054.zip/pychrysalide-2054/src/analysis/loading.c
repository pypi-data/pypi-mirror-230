
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.c - reconnaissance de contenus binaires
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


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "../core/global.h"
#include "../glibext/chrysamarshal.h"
#include "../glibext/delayed-int.h"
#include "../plugins/pglist.h"



/* ------------------------- TACHE D'EXPLORATION DE CONTENU ------------------------- */


#define G_TYPE_EXPLORING_WORK            g_exploring_work_get_type()
#define G_EXPLORING_WORK(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_EXPLORING_WORK, GExploringWork))
#define G_IS_EXPLORING_WORK(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_EXPLORING_WORK))
#define G_EXPLORING_WORK_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_EXPLORING_WORK, GExploringWorkClass))
#define G_IS_EXPLORING_WORK_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_EXPLORING_WORK))
#define G_EXPLORING_WORK_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_EXPLORING_WORK, GExploringWorkClass))


/* Conversion de contenu binaire en contenu chargé (instance) */
typedef struct _GExploringWork
{
    GDelayedWork parent;                    /* A laisser en premier        */

    wgroup_id_t wid;                        /* Groupe d'appartenance       */
#ifndef NDEBUG
    bool wid_defined;                       /* Validation de l'identifiant */
#endif

    GBinContent *content;                   /* Contenu brut à disposition  */

} GExploringWork;

/* Conversion de contenu binaire en contenu chargé (classe) */
typedef struct _GExploringWorkClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GExploringWorkClass;


/* Indique le type défini pour l'exploration de contenu binaire. */
GType g_exploring_work_get_type(void);

/* Initialise la classe des tâches d'exploration de contenu. */
static void g_exploring_work_class_init(GExploringWorkClass *);

/* Initialise une tâche d'exploration de contenu. */
static void g_exploring_work_init(GExploringWork *);

/* Supprime toutes les références externes. */
static void g_exploring_work_dispose(GExploringWork *);

/* Procède à la libération totale de la mémoire. */
static void g_exploring_work_finalize(GExploringWork *);

/* Prépare la conversion non bloquée d'un contenu binaire. */
static GExploringWork *g_exploring_work_new(GBinContent *);

/* Fournit l'identifiant du groupe de rattachement de la tâche. */
static wgroup_id_t g_exploring_work_get_group_id(const GExploringWork *);

/* Définit l'identifiant du groupe de rattachement de la tâche. */
static void g_exploring_work_set_group_id(GExploringWork *, wgroup_id_t);

/* Réalise l'exploration effective de formes de contenus. */
static void g_exploring_work_process(GExploringWork *, GtkStatusStack *);



/* --------------------- EXPLORATION NON BLOQUANTE DES CONTENUS --------------------- */


/* Regroupement des chargements */
typedef struct _exploring_group
{
    GBinContent *original;                  /* Contenu binaire initial     */

    size_t remaining;                       /* Nombre de tâches restantes  */

    wgroup_id_t wid;                        /* Groupe d'appartenance       */

    GBinContent **contents;                 /* Contenus reconnus dispos.   */
    size_t count;                           /* Taille de cette liste       */

} exploring_group;

/* Exploration de contenus binaires (instance) */
struct _GContentExplorer
{
    GObject parent;                         /* A laisser en premier        */

    exploring_group *groups;                /* Rassemblement de chargements*/
    size_t count;                           /* Nombre de ces groupes       */
    GMutex mutex;                           /* Accès protégé à la liste    */

};

/* Exploration de contenus binaires (classe) */
struct _GContentExplorerClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* explored) (GContentExplorer *, wgroup_id_t);

};


/* Initialise la classe les explorations de contenus binaires. */
static void g_content_explorer_class_init(GContentExplorerClass *);

/* Initialise une exploration de contenus binaires. */
static void g_content_explorer_init(GContentExplorer *);

/* Supprime toutes les références externes. */
static void g_content_explorer_dispose(GContentExplorer *);

/* Procède à la libération totale de la mémoire. */
static void g_content_explorer_finalize(GContentExplorer *);

/* Retrouve le groupe correspondant à un identifiant donné. */
static exploring_group *g_content_explorer_find_group(GContentExplorer *, wgroup_id_t);

/* Note la fin d'une phase d'exploration de contenu. */
static void g_content_explorer_ack(GContentExplorer *, GExploringWork *);



/* ------------------------- TACHE DE RESOLUTION DE CONTENU ------------------------- */


#define G_TYPE_RESOLVING_WORK            g_resolving_work_get_type()
#define G_RESOLVING_WORK(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RESOLVING_WORK, GResolvingWork))
#define G_IS_RESOLVING_WORK(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RESOLVING_WORK))
#define G_RESOLVING_WORK_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RESOLVING_WORK, GResolvingWorkClass))
#define G_IS_RESOLVING_WORK_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RESOLVING_WORK))
#define G_RESOLVING_WORK_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RESOLVING_WORK, GResolvingWorkClass))


/* Conversion de contenu binaire en contenu chargé (instance) */
typedef struct _GResolvingWork
{
    GDelayedWork parent;                    /* A laisser en premier        */

    wgroup_id_t wid;                        /* Groupe d'appartenance       */
#ifndef NDEBUG
    bool wid_defined;                       /* Validation de l'identifiant */
#endif

    GBinContent *content;                   /* Contenu brut à disposition  */

} GResolvingWork;

/* Conversion de contenu binaire en contenu chargé (classe) */
typedef struct _GResolvingWorkClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GResolvingWorkClass;


/* Indique le type défini pour la conversion de contenu binaire en contenu chargé. */
GType g_resolving_work_get_type(void);

/* Initialise la classe des tâches de conversion de contenu. */
static void g_resolving_work_class_init(GResolvingWorkClass *);

/* Initialise une tâche de conversion de contenu. */
static void g_resolving_work_init(GResolvingWork *);

/* Supprime toutes les références externes. */
static void g_resolving_work_dispose(GResolvingWork *);

/* Procède à la libération totale de la mémoire. */
static void g_resolving_work_finalize(GResolvingWork *);

/* Prépare la conversion non bloquée d'un contenu binaire. */
static GResolvingWork *g_resolving_work_new(GBinContent *);

/* Fournit l'identifiant du groupe de rattachement de la tâche. */
static wgroup_id_t g_resolving_work_get_group_id(const GResolvingWork *);

/* Définit l'identifiant du groupe de rattachement de la tâche. */
static void g_resolving_work_set_group_id(GResolvingWork *, wgroup_id_t);

/* Réalise la conversion effective de formes de contenus. */
static void g_resolving_work_process(GResolvingWork *, GtkStatusStack *);



/* ------------------- RESOLUTION DE CONTENUS BINAIRES EN CHARGES ------------------- */


/* Regroupement des chargements */
typedef struct _resolving_group
{
    size_t remaining;                       /* Nombre de tâches restantes  */

    wgroup_id_t wid;                        /* Groupe d'appartenance       */

    GLoadedContent **loaded;                /* Contenus reconnus à intégrer*/
    size_t count;                           /* Taille de cette liste       */

} resolving_group;

/* Résolution de contenus binaires en formats chargés (instance) */
struct _GContentResolver
{
    GObject parent;                         /* A laisser en premier        */

    resolving_group *groups;                /* Rassemblement de chargements*/
    size_t count;                           /* Nombre de ces groupes       */
    GMutex mutex;                           /* Accès protégé à la liste    */

};

/* Résolution de contenus binaires en formats chargés (classe) */
struct _GContentResolverClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* resolved) (GContentResolver *, wgroup_id_t);

};


/* Initialise la classe des résolutions de contenus binaires. */
static void g_content_resolver_class_init(GContentResolverClass *);

/* Initialise une résolution de contenus binaires. */
static void g_content_resolver_init(GContentResolver *);

/* Supprime toutes les références externes. */
static void g_content_resolver_dispose(GContentResolver *);

/* Procède à la libération totale de la mémoire. */
static void g_content_resolver_finalize(GContentResolver *);

/* Retrouve le groupe correspondant à un identifiant donné. */
static resolving_group *g_content_resolver_find_group(GContentResolver *, wgroup_id_t);

/* Note la fin d'une phase de resolution de contenu. */
static void g_content_resolver_ack(GContentResolver *, GResolvingWork *);



/* ---------------------------------------------------------------------------------- */
/*                           TACHE D'EXPLORATION DE CONTENU                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour l'exploration de contenu binaire. */
G_DEFINE_TYPE(GExploringWork, g_exploring_work, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches d'exploration de contenu.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_exploring_work_class_init(GExploringWorkClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_exploring_work_dispose;
    object->finalize = (GObjectFinalizeFunc)g_exploring_work_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_exploring_work_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une tâche d'exploration de contenu.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_exploring_work_init(GExploringWork *work)
{
#ifndef NDEBUG
    work->wid_defined = false;
#endif

    work->content = NULL;

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

static void g_exploring_work_dispose(GExploringWork *work)
{
    g_clear_object(&work->content);

    G_OBJECT_CLASS(g_exploring_work_parent_class)->dispose(G_OBJECT(work));

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

static void g_exploring_work_finalize(GExploringWork *work)
{
    G_OBJECT_CLASS(g_exploring_work_parent_class)->finalize(G_OBJECT(work));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire disponible pour traitements.       *
*                                                                             *
*  Description : Prépare l'exploration non bloquée d'un contenu binaire.      *
*                                                                             *
*  Retour      : Tâche de travail mise en place.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GExploringWork *g_exploring_work_new(GBinContent *content)
{
    GExploringWork *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_EXPLORING_WORK, NULL);

    result->content = content;
    g_object_ref(G_OBJECT(content));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit l'identifiant du groupe de rattachement de la tâche. *
*                                                                             *
*  Retour      : Identifiant d'un même ensemble d'explorations.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static wgroup_id_t g_exploring_work_get_group_id(const GExploringWork *work)
{
    wgroup_id_t result;                     /* Identifiant à retourner     */

    assert(work->wid_defined);

    result = work->wid;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à compléter.                                 *
*                wid  = identifiant d'un même ensemble d'explorations.        *
*                                                                             *
*  Description : Définit l'identifiant du groupe de rattachement de la tâche. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_exploring_work_set_group_id(GExploringWork *work, wgroup_id_t wid)
{
#ifndef NDEBUG
    work->wid_defined = true;
#endif

    work->wid = wid;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work   = encadrement de conversion à mener.                  *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Réalise l'exploration effective de formes de contenus.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_exploring_work_process(GExploringWork *work, GtkStatusStack *status)
{
    wgroup_id_t wid;                        /* Groupe d'appartenance       */

    wid = g_exploring_work_get_group_id(work);

    handle_binary_content(PGA_CONTENT_EXPLORER, work->content, wid, status);

}



/* ---------------------------------------------------------------------------------- */
/*                       EXPLORATION NON BLOQUANTE DES CONTENUS                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour l'exploration de contenus binaires. */
G_DEFINE_TYPE(GContentExplorer, g_content_explorer, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe les explorations de contenus binaires.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_explorer_class_init(GContentExplorerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_content_explorer_dispose;
    object->finalize = (GObjectFinalizeFunc)g_content_explorer_finalize;

    g_signal_new("explored",
                 G_TYPE_CONTENT_EXPLORER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GContentExplorerClass, explored),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__UINT64,
                 G_TYPE_NONE, 1, G_TYPE_UINT64);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une exploration de contenus binaires.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_explorer_init(GContentExplorer *explorer)
{
    explorer->groups = NULL;
    explorer->count = 0;

    g_mutex_init(&explorer->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_explorer_dispose(GContentExplorer *explorer)
{
    while (explorer->count > 0)
        g_content_explorer_delete_group(explorer, explorer->groups[0].wid);

    if (explorer->groups != NULL)
        free(explorer->groups);

    g_mutex_clear(&explorer->mutex);

    G_OBJECT_CLASS(g_content_explorer_parent_class)->dispose(G_OBJECT(explorer));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_explorer_finalize(GContentExplorer *explorer)
{
    G_OBJECT_CLASS(g_content_explorer_parent_class)->finalize(G_OBJECT(explorer));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un gestionnaire des explorations de contenus binaires.  *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentExplorer *g_content_explorer_new(void)
{
    GContentExplorer *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_CONTENT_EXPLORER, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à consulter.          *
*                wid      = identifiant du groupe recherché.                  *
*                                                                             *
*  Description : Retrouve le groupe correspondant à un identifiant donné.     *
*                                                                             *
*  Retour      : Groupe trouvé ou NULL en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static exploring_group *g_content_explorer_find_group(GContentExplorer *explorer, wgroup_id_t wid)
{
    exploring_group *result;            /* Trouvaille à retourner      */
    size_t i;                           /* Boucle de parcours          */

    assert(!g_mutex_trylock(&explorer->mutex));

    result = NULL;

    for (i = 0; i < explorer->count && result == NULL; i++)
        if (explorer->groups[i].wid == wid)
            result = &explorer->groups[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à consulter.          *
*                work     = exploration qui vient de se terminer.             *
*                                                                             *
*  Description : Note la fin d'une phase d'exploration de contenu.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_explorer_ack(GContentExplorer *explorer, GExploringWork *work)
{
    wgroup_id_t wid;                        /* Groupe d'appartenance       */
    exploring_group *group;                 /* Groupe d'opération concerné */
    bool empty;                             /* Fin de l'exploration ?      */

    wid = g_exploring_work_get_group_id(work);

    g_mutex_lock(&explorer->mutex);

    group = g_content_explorer_find_group(explorer, wid);
    assert(group != NULL);

    assert(group->remaining > 0);

    empty = (--group->remaining == 0);

    g_mutex_unlock(&explorer->mutex);

    if (empty)
        g_signal_emit_by_name(explorer, "explored", wid);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à manipuler.          *
*                content  = contenu initial à découvrir.                      *
*                                                                             *
*  Description : Initie une nouvelle vague d'exploration de contenu.          *
*                                                                             *
*  Retour      : Identifiant du nouveau groupe mis en place.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t g_content_explorer_create_group(GContentExplorer *explorer, GBinContent *content)
{
    wgroup_id_t result;                     /* Identifiant à retourner     */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    exploring_group *group;                 /* Groupe ciblé par l'opération*/
    GExploringWork *work;                   /* Nouvelle vague d'exploration*/

    g_mutex_lock(&explorer->mutex);

    /* Récupération d'un identifiant libre */

    queue = get_work_queue();

    result = g_work_queue_define_work_group(queue);

#ifndef NDEBUG
    group = g_content_explorer_find_group(explorer, result);
    assert(group == NULL);
#endif

    /* Mise en place du groupe */

    explorer->groups = (exploring_group *)realloc(explorer->groups, ++explorer->count * sizeof(exploring_group));

    group = &explorer->groups[explorer->count - 1];

    group->original = content;
    g_object_ref(G_OBJECT(content));

    group->remaining = 1;

    group->wid = result;

    group->contents = NULL;
    group->count = 0;

    /* Alimentation du contenu initial */

    work = g_exploring_work_new(content);
    g_exploring_work_set_group_id(work, result);

    g_signal_connect_swapped(work, "work-completed", G_CALLBACK(g_content_explorer_ack), explorer);

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(work), result);

    g_mutex_unlock(&explorer->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à manipuler.          *
*                wid      = identifiant du groupe à supprimer.                *
*                                                                             *
*  Description : Termine une vague d'exploration de contenu.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_content_explorer_delete_group(GContentExplorer *explorer, wgroup_id_t wid)
{
    exploring_group *group;                 /* Groupe ciblé par l'opération*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    size_t i;                               /* Boucle de parcours          */
    size_t index;                           /* Indice des paramètres       */

    g_mutex_lock(&explorer->mutex);

    group = g_content_explorer_find_group(explorer, wid);
    assert(group != NULL);

    /* Supression des contenus chargés */

    queue = get_work_queue();

    g_work_queue_delete_work_group(queue, group->wid);

    g_object_unref(G_OBJECT(group->original));

    for (i = 0; i < group->count; i++)
        g_object_unref(G_OBJECT(group->contents[i]));

    if (group->contents != NULL)
        free(group->contents);

    /* Réorganisation de la liste */

    index = group - explorer->groups;

    if ((index + 1) < explorer->count)
        memmove(&explorer->groups[index], &explorer->groups[index + 1],
                (explorer->count - index - 1) * sizeof(exploring_group));

    explorer->groups = realloc(explorer->groups, --explorer->count * sizeof(exploring_group));

    /* Sortie */

    g_mutex_unlock(&explorer->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à consulter.          *
*                wid      = identifiant du groupe à parcourir.                *
*                content  = nouveau contenu à intégrer.                       *
*                                                                             *
*  Description : Ajoute un nouveau contenu découvert au crédit d'un groupe.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : La propritété du contenu fourni est cédée.                   *
*                                                                             *
******************************************************************************/

void g_content_explorer_populate_group(GContentExplorer *explorer, wgroup_id_t wid, GBinContent *content)
{
    exploring_group *group;                 /* Groupe d'opération concerné */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    GExploringWork *work;                   /* Nouvelle vague d'exploration*/

    g_mutex_lock(&explorer->mutex);

    group = g_content_explorer_find_group(explorer, wid);
    assert(group != NULL);

    /* Conservation du résultat */

    group->contents = realloc(group->contents, ++group->count * sizeof(GBinContent *));

    group->contents[group->count - 1] = content;
    g_object_ref_sink(G_OBJECT(content));

    /* Relancement des explorations */

    group->remaining++;

    work = g_exploring_work_new(content);
    g_exploring_work_set_group_id(work, group->wid);

    g_signal_connect_swapped(work, "work-completed", G_CALLBACK(g_content_explorer_ack), explorer);

    queue = get_work_queue();

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(work), group->wid);

    g_mutex_unlock(&explorer->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à consulter.          *
*                wid      = identifiant du groupe à parcourir.                *
*                count    = nombre de contenus binaires retournés. [OUT]      *
*                                                                             *
*  Description : Fournit la liste de tous les contenus disponibles.           *
*                                                                             *
*  Retour      : Liste de contenus binaires enregistrés.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent **g_content_explorer_get_all(GContentExplorer *explorer, wgroup_id_t wid, size_t *count)
{
    GBinContent **result;                   /* Trouvailles à retourner      */
    exploring_group *group;                 /* Groupe d'opération concerné */
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&explorer->mutex);

    group = g_content_explorer_find_group(explorer, wid);
    assert(group != NULL);

    /* Allocation de la liste finale */

    *count = 1 + group->count;
    result = malloc(*count * sizeof(GBinContent *));

    /* On regarde déjà du côté de la source */

    result[0] = group->original;

    g_object_ref(G_OBJECT(result[0]));

    /* On parcourt les éventuels contenus encapsulés découverts */

    for (i = 0; i < group->count; i++)
    {
        result[1 + i] = group->contents[i];

        g_object_ref(G_OBJECT(result[1 + i]));

    }

    g_mutex_unlock(&explorer->mutex);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           TACHE DE RESOLUTION DE CONTENU                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour la conversion de contenu binaire en contenu chargé. */
G_DEFINE_TYPE(GResolvingWork, g_resolving_work, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches de conversion de contenu.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_resolving_work_class_init(GResolvingWorkClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_resolving_work_dispose;
    object->finalize = (GObjectFinalizeFunc)g_resolving_work_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_resolving_work_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une tâche de conversion de contenu.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_resolving_work_init(GResolvingWork *work)
{
#ifndef NDEBUG
    work->wid_defined = false;
#endif

    work->content = NULL;

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

static void g_resolving_work_dispose(GResolvingWork *work)
{
    g_clear_object(&work->content);

    G_OBJECT_CLASS(g_resolving_work_parent_class)->dispose(G_OBJECT(work));

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

static void g_resolving_work_finalize(GResolvingWork *work)
{
    G_OBJECT_CLASS(g_resolving_work_parent_class)->finalize(G_OBJECT(work));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire disponible pour traitements.       *
*                                                                             *
*  Description : Prépare la conversion non bloquée d'un contenu binaire.      *
*                                                                             *
*  Retour      : Tâche de travail mise en place.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GResolvingWork *g_resolving_work_new(GBinContent *content)
{
    GResolvingWork *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_RESOLVING_WORK, NULL);

    result->content = content;
    g_object_ref(G_OBJECT(content));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit l'identifiant du groupe de rattachement de la tâche. *
*                                                                             *
*  Retour      : Identifiant d'un même ensemble de conversions.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static wgroup_id_t g_resolving_work_get_group_id(const GResolvingWork *work)
{
    wgroup_id_t result;                     /* Identifiant à retourner     */

    assert(work->wid_defined);

    result = work->wid;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à compléter.                                 *
*                wid  = identifiant d'un même ensemble de conversions.        *
*                                                                             *
*  Description : Définit l'identifiant du groupe de rattachement de la tâche. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_resolving_work_set_group_id(GResolvingWork *work, wgroup_id_t wid)
{
#ifndef NDEBUG
    work->wid_defined = true;
#endif

    work->wid = wid;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work   = encadrement de conversion à mener.                  *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Réalise la conversion effective de formes de contenus.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_resolving_work_process(GResolvingWork *work, GtkStatusStack *status)
{
    wgroup_id_t wid;                        /* Groupe d'appartenance       */

    wid = g_resolving_work_get_group_id(work);

    handle_binary_content(PGA_CONTENT_RESOLVER, work->content, wid, status);

}



/* ---------------------------------------------------------------------------------- */
/*                     RESOLUTION DE CONTENUS BINAIRES EN CHARGES                     */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour la résolution de contenus binaires en formats chargés. */
G_DEFINE_TYPE(GContentResolver, g_content_resolver, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des résolutions de contenus binaires.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_resolver_class_init(GContentResolverClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_content_resolver_dispose;
    object->finalize = (GObjectFinalizeFunc)g_content_resolver_finalize;

    g_signal_new("resolved",
                 G_TYPE_CONTENT_RESOLVER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GContentResolverClass, resolved),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__UINT64,
                 G_TYPE_NONE, 1, G_TYPE_UINT64);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une résolution de contenus binaires.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_resolver_init(GContentResolver *resolver)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_resolver_dispose(GContentResolver *resolver)
{
    while (resolver->count > 0)
        g_content_resolver_delete_group(resolver, resolver->groups[0].wid);

    if (resolver->groups != NULL)
        free(resolver->groups);

    g_mutex_clear(&resolver->mutex);

    G_OBJECT_CLASS(g_content_resolver_parent_class)->dispose(G_OBJECT(resolver));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_resolver_finalize(GContentResolver *resolver)
{
    G_OBJECT_CLASS(g_content_resolver_parent_class)->finalize(G_OBJECT(resolver));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un gestionnaire des résolutions de contenus binaires.   *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentResolver *g_content_resolver_new(void)
{
    GContentResolver *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_CONTENT_RESOLVER, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire de résolutions à consulter.          *
*                wid      = identifiant du groupe recherché.                  *
*                                                                             *
*  Description : Retrouve le groupe correspondant à un identifiant donné.     *
*                                                                             *
*  Retour      : Groupe trouvé ou NULL en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static resolving_group *g_content_resolver_find_group(GContentResolver *resolver, wgroup_id_t wid)
{
    resolving_group *result;            /* Trouvaille à retourner      */
    size_t i;                           /* Boucle de parcours          */

    assert(!g_mutex_trylock(&resolver->mutex));

    result = NULL;

    for (i = 0; i < resolver->count && result == NULL; i++)
        if (resolver->groups[i].wid == wid)
            result = &resolver->groups[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire de résolutions à consulter.          *
*                work     = resolvation qui vient de se terminer.             *
*                                                                             *
*  Description : Note la fin d'une phase de resolution de contenu.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_resolver_ack(GContentResolver *resolver, GResolvingWork *work)
{
    wgroup_id_t wid;                        /* Groupe d'appartenance       */
    resolving_group *group;                 /* Groupe d'opération concerné */
    bool empty;                             /* Fin de l'resolvation ?      */

    wid = g_resolving_work_get_group_id(work);

    g_mutex_lock(&resolver->mutex);

    group = g_content_resolver_find_group(resolver, wid);
    assert(group != NULL);

    assert(group->remaining > 0);

    empty = (--group->remaining == 0);

    g_mutex_unlock(&resolver->mutex);

    if (empty)
        g_signal_emit_by_name(resolver, "resolved", wid);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire de résolutions à manipuler.          *
*                wid      = identifiant du groupe de tâches réservé.          *
*                contents = contenus à analyser.                              *
*                count    = nombre de ces contenus.                           *
*                                                                             *
*  Description : Initie une nouvelle vague de résolution de contenus.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_content_resolver_create_group(GContentResolver *resolver, wgroup_id_t wid, GBinContent **contents, size_t count)
{
    resolving_group *group;                 /* Groupe ciblé par l'opération*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    size_t i;                               /* Boucle de parcours          */
    GResolvingWork *work;                   /* Nouvelle vague de résolution*/

    g_mutex_lock(&resolver->mutex);

    /* Mise en place du groupe */

    resolver->groups = (resolving_group *)realloc(resolver->groups, ++resolver->count * sizeof(resolving_group));

    group = &resolver->groups[resolver->count - 1];

    group->remaining = count;

    group->wid = wid;

    group->loaded = NULL;
    group->count = 0;

    /* Alimentation du contenu initial */

    queue = get_work_queue();

    for (i = 0; i < count; i++)
    {
        work = g_resolving_work_new(contents[i]);
        g_resolving_work_set_group_id(work, wid);

        g_signal_connect_swapped(work, "work-completed", G_CALLBACK(g_content_resolver_ack), resolver);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(work), wid);

    }

    g_mutex_unlock(&resolver->mutex);

    if (count == 0)
        g_signal_emit_by_name(resolver, "resolved", wid);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire d'explorations à manipuler.          *
*                wid      = identifiant du groupe à supprimer.                *
*                                                                             *
*  Description : Termine une vague de résolution de contenu.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_content_resolver_delete_group(GContentResolver *resolver, wgroup_id_t wid)
{
    resolving_group *group;                 /* Groupe ciblé par l'opération*/
    size_t i;                               /* Boucle de parcours          */
    size_t index;                           /* Indice des paramètres       */

    g_mutex_lock(&resolver->mutex);

    group = g_content_resolver_find_group(resolver, wid);

    /* Supression des contenus chargés */

    for (i = 0; i < group->count; i++)
        g_object_unref(G_OBJECT(group->loaded[i]));

    if (group->loaded != NULL)
        free(group->loaded);

    /* Réorganisation de la liste */

    index = group - resolver->groups;

    if ((index + 1) < resolver->count)
        memmove(&resolver->groups[index], &resolver->groups[index + 1],
                (resolver->count - index - 1) * sizeof(resolving_group));

    resolver->groups = realloc(resolver->groups, --resolver->count * sizeof(resolving_group));

    /* Sortie */

    g_mutex_unlock(&resolver->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire de résolutions à consulter.          *
*                wid      = identifiant du groupe recherché.                  *
*                loaded   = contenu chargé et pouvant être représenté.        *
*                                                                             *
*  Description : Intègre un contenu chargé dans les résultats.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_content_resolver_add_detected(GContentResolver *resolver, wgroup_id_t wid, GLoadedContent *loaded)
{
    resolving_group *group;                 /* Groupe ciblé par l'opération*/

    g_mutex_lock(&resolver->mutex);

    group = g_content_resolver_find_group(resolver, wid);
    assert(group != NULL);

    group->loaded = realloc(group->loaded, ++group->count * sizeof(GLoadedContent *));

    group->loaded[group->count - 1] = loaded;
    g_object_ref(G_OBJECT(loaded));

    g_mutex_unlock(&resolver->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire de resolutions à consulter.          *
*                wid      = identifiant du groupe à parcourir.                *
*                count    = nombre de contenus binaires retournés. [OUT]      *
*                                                                             *
*  Description : Fournit la liste de tous les contenus chargés valables.      *
*                                                                             *
*  Retour      : Liste de contenus chargés enregistrés.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedContent **g_content_resolver_get_all(GContentResolver *resolver, wgroup_id_t wid, size_t *count)
{
    GLoadedContent **result;                /* Trouvailles à retourner      */
    resolving_group *group;                 /* Groupe d'opération concerné */
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&resolver->mutex);

    group = g_content_resolver_find_group(resolver, wid);
    assert(group != NULL);

    /* Allocation de la liste finale */

    *count = group->count;
    result = malloc(*count * sizeof(GLoadedContent *));

    /* On parcourt les éventuels contenus encapsulés découverts */

    for (i = 0; i < group->count; i++)
    {
        result[i] = group->loaded[i];

        g_object_ref(G_OBJECT(result[i]));

    }

    g_mutex_unlock(&resolver->mutex);

    return result;

}
