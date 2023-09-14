
/* Chrysalide - Outil d'analyse de fichiers binaires
 * updating.c - mise à jour des panneaux de l'interface
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "updating.h"


#include <malloc.h>


#include "updating-int.h"
#include "../../core/global.h"
#include "../../glibext/delayed-int.h"
#include "../../glibext/signal.h"



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Procède à l'initialisation de l'interface de mise à jour. */
static void g_updatable_panel_default_init(GUpdatablePanelInterface *);



/* ---------------------------- AIDE POUR LA MISE A JOUR ---------------------------- */


/* Procédure de mise à jour de panneau graphique (instance) */
struct _GPanelUpdate
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GUpdatablePanel *panel;                 /* Panneau à manipuler         */
    unsigned int uid;                       /* Identifiant complémentaire  */

    size_t max;                             /* Marge de progression finale */
    void *data;                             /* Données utiles au traitement*/
    char *msg;                              /* Description d'activité      */

};

/* Procédure de mise à jour de panneau graphique (classe) */
struct _GPanelUpdateClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches des mises à jour de panneaux. */
static void g_panel_update_class_init(GPanelUpdateClass *);

/* Initialise une tâche d'étude de mise à jour. */
static void g_panel_update_init(GPanelUpdate *);

/* Supprime toutes les références externes. */
static void g_panel_update_dispose(GPanelUpdate *);

/* Procède à la libération totale de la mémoire. */
static void g_panel_update_finalize(GPanelUpdate *);

/* Assure la mise à jour d'un panneau en différé. */
static void g_panel_update_process(GPanelUpdate *, GtkStatusStack *);

/* Marque l'achèvement d'une mise à jour de panneau. */
static void conclude_panel_update(GPanelUpdate *, GUpdatablePanel *);



/* ---------------------------------------------------------------------------------- */
/*                        MECANISMES DE MISE A JOUR DE PANNEAU                        */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type d'une interface pour la mise à jour de panneau. */
G_DEFINE_INTERFACE(GUpdatablePanel, g_updatable_panel, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de mise à jour.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_updatable_panel_default_init(GUpdatablePanelInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                count = nombre d'étapes à prévoir dans le traitement. [OUT]  *
*                data  = données sur lesquelles s'appuyer ensuite. [OUT]      *
*                msg   = description du message d'information. [OUT]          *
*                                                                             *
*  Description : Prépare une opération de mise à jour de panneau.             *
*                                                                             *
*  Retour      : Bilan de la préparation.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_updatable_panel_setup(const GUpdatablePanel *panel, unsigned int uid, size_t *count, void **data, char **msg)
{
    bool result;                            /* Bilan à retourner           */
    GUpdatablePanelIface *iface;            /* Interface utilisée          */

    iface = G_UPDATABLE_PANEL_GET_IFACE(panel);

    *count = 0;
    *data = NULL;
    *msg = NULL;

    result = iface->setup(panel, uid, count, data, msg);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                                                                             *
*  Description : Obtient le groupe de travail dédié à une mise à jour.        *
*                                                                             *
*  Retour      : Identifiant de groupe de travail.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t g_updatable_panel_get_group(const GUpdatablePanel *panel)
{
    wgroup_id_t result;                     /* Identifiant à retourner     */
    GUpdatablePanelIface *iface;            /* Interface utilisée          */

    iface = G_UPDATABLE_PANEL_GET_IFACE(panel);

    result = iface->get_group(panel);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données préparées par l'appelant.                    *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau avant mise à jour.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Cette fonction est appelée depuis le contexte principal.     *
*                                                                             *
******************************************************************************/

void g_updatable_panel_introduce(const GUpdatablePanel *panel, unsigned int uid, void *data)
{
    GUpdatablePanelIface *iface;            /* Interface utilisée          */

    iface = G_UPDATABLE_PANEL_GET_IFACE(panel);

    iface->introduce(panel, uid, data);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau ciblé par une mise à jour.                  *
*                uid    = identifiant de la phase de traitement.              *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données préparées par l'appelant.                   *
*                                                                             *
*  Description : Réalise une opération de mise à jour de panneau.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_updatable_panel_process(const GUpdatablePanel *panel, unsigned int uid, GtkStatusStack *status, activity_id_t id, void *data)
{
    GUpdatablePanelIface *iface;            /* Interface utilisée          */

    iface = G_UPDATABLE_PANEL_GET_IFACE(panel);

    iface->process(panel, uid, status, id, data);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données préparées par l'appelant.                    *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau après mise à jour.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Cette fonction est appelée depuis le contexte principal.     *
*                                                                             *
******************************************************************************/

void g_updatable_panel_conclude(GUpdatablePanel *panel, unsigned int uid, void *data)
{
    GUpdatablePanelIface *iface;            /* Interface utilisée          */

    iface = G_UPDATABLE_PANEL_GET_IFACE(panel);

    iface->conclude(panel, uid, data);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données en place à nettoyer avant suppression.       *
*                                                                             *
*  Description : Supprime les données dynamiques utilisées à la mise à jour.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_updatable_panel_clean_data(const GUpdatablePanel *panel, unsigned int uid, void *data)
{
    GUpdatablePanelIface *iface;            /* Interface utilisée          */

    iface = G_UPDATABLE_PANEL_GET_IFACE(panel);

    if (iface->clean != NULL && data != NULL)
        iface->clean(panel, uid, data);

}



/* ---------------------------------------------------------------------------------- */
/*                              AIDE POUR LA MISE A JOUR                              */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les tâches de mise à jour de panneau. */
G_DEFINE_TYPE(GPanelUpdate, g_panel_update, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches des mises à jour de panneaux.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_update_class_init(GPanelUpdateClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_panel_update_dispose;
    object->finalize = (GObjectFinalizeFunc)g_panel_update_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_panel_update_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une tâche d'étude de mise à jour.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_update_init(GPanelUpdate *update)
{
    update->panel = NULL;
    update->uid = -1;

    update->max = 0;
    update->data = NULL;
    update->msg = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_update_dispose(GPanelUpdate *update)
{
    if (update->panel != NULL)
        g_updatable_panel_clean_data(update->panel, update->uid, update->data);

    g_clear_object(&update->panel);

    G_OBJECT_CLASS(g_panel_update_parent_class)->dispose(G_OBJECT(update));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_update_finalize(GPanelUpdate *update)
{
    if (update->data != NULL)
        free(update->data);

    if (update->msg != NULL)
        free(update->msg);

    G_OBJECT_CLASS(g_panel_update_parent_class)->finalize(G_OBJECT(update));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = interface permettant une mise à jour de panneau.     *
*                uid   = identifiant à associer à la procédure.               *
*                                                                             *
*  Description : Crée une tâche de mise à jour non bloquante.                 *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelUpdate *g_panel_update_new(GUpdatablePanel *panel, unsigned int uid)
{
    GPanelUpdate *result;                   /* Tâche à retourner           */
    bool status;                            /* Bilan de la préparation     */

    result = g_object_new(G_TYPE_PANEL_UPDATE, NULL);

    g_object_ref(G_OBJECT(panel));
    result->panel = panel;

    result->uid = uid;

    status = g_updatable_panel_setup(panel, uid, &result->max, &result->data, &result->msg);

    if (!status)
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = opération de mise à jour à mener.                   *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure la mise à jour d'un panneau en différé.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_update_process(GPanelUpdate *update, GtkStatusStack *status)
{
    activity_id_t id;                       /* Identifiant de progression  */

    id = gtk_status_stack_add_activity(status, update->msg, update->max);

    g_updatable_panel_process(update->panel, update->uid, status, id, update->data);

    gtk_status_stack_remove_activity(status, id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = tâche venant de se terminer.                        *
*                panel  = interface visée par la procédure.                   *
*                                                                             *
*  Description : Marque l'achèvement d'une mise à jour de panneau.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void conclude_panel_update(GPanelUpdate *update, GUpdatablePanel *panel)
{
    g_updatable_panel_conclude(panel, update->uid, update->data);

}



/* ---------------------------------------------------------------------------------- */
/*                            ENCAPSULATION DE HAUT NIVEAU                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = interface permettant une mise à jour de panneau.     *
*                uid   = identifiant à associer à la procédure.               *
*                                                                             *
*  Description : Prépare et lance l'actualisation d'un panneau.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Cette fonction est à appeler depuis le contexte principal.   *
*                                                                             *
******************************************************************************/

void run_panel_update(GUpdatablePanel *panel, unsigned int uid)
{
    GWorkQueue *queue;                      /* Gestionnaire de tâches      */
    wgroup_id_t gid;                        /* Groupe de travail à utiliser*/
    GPanelUpdate *update;                   /* Procédure de mise à jour    */

    update = g_panel_update_new(panel, uid);

    if (update != NULL)
    {
        g_signal_connect_to_main(update, "work-completed", G_CALLBACK(conclude_panel_update), panel,
                                 g_cclosure_marshal_VOID__VOID);

        g_updatable_panel_introduce(panel, uid, update->data);

        queue = get_work_queue();

        gid = g_updatable_panel_get_group(panel);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(update), gid);

    }

}
