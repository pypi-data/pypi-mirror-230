
/* Chrysalide - Outil d'analyse de fichiers binaires
 * seq.c - constitution d'un traitement séquentiel générique
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


#include "seq.h"


#include "delayed-int.h"



/* Type de travail fractionné */
typedef enum _SeqWorkType
{
    SWT_SIMPLE,                             /* Traitement de masse         */
    SWT_BOOLEAN,                            /* Retour booléen attendu      */
    SWT_OBJECT,                             /* Objet référencé à libérer   */

} SeqWorkType;

/* Portion de traitement séquentiel à mener (instance) */
struct _GSeqWork
{
    GDelayedWork parent;                    /* A laisser en premier        */

    void *data;                             /* Données pour l'utilisateur  */

    size_t begin;                           /* Point de départ du parcours */
    size_t end;                             /* Point d'arrivée exclu       */

    activity_id_t id;                       /* Identifiant pour messages   */

    SeqWorkType type;                       /* Sélection du sous-traitant  */

    union
    {
        seq_work_cb void_cb;                /* Traitement simple           */
        seq_work_bool_cb bool_cb;           /* Traitement et retour booléen*/
        seq_work_obj_cb obj_cb;             /* Traitement + objet référencé*/

    } callback;

    bool *status;                           /* Bilan global constitué      */

};

/* Portion de traitement séquentiel à mener (classe) */
struct _GSeqWorkClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches des traitements séquentiels. */
static void g_seq_work_class_init(GSeqWorkClass *);

/* Initialise une tâche de traitement séquentiel et partiel. */
static void g_seq_work_init(GSeqWork *);

/* Supprime toutes les références externes. */
static void g_seq_work_dispose(GSeqWork *);

/* Procède à la libération totale de la mémoire. */
static void g_seq_work_finalize(GSeqWork *);

/* Assure le chargement pour un format DEX en différé. */
static void g_seq_work_process(GSeqWork *, GtkStatusStack *);



/* Indique le type défini pour les tâches de traitement séquentiel et partiel. */
G_DEFINE_TYPE(GSeqWork, g_seq_work, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches des traitements séquentiels. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_seq_work_class_init(GSeqWorkClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_seq_work_dispose;
    object->finalize = (GObjectFinalizeFunc)g_seq_work_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_seq_work_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une tâche de traitement séquentiel et partiel.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_seq_work_init(GSeqWork *work)
{

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

static void g_seq_work_dispose(GSeqWork *work)
{
    G_OBJECT_CLASS(g_seq_work_parent_class)->dispose(G_OBJECT(work));

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

static void g_seq_work_finalize(GSeqWork *work)
{
    G_OBJECT_CLASS(g_seq_work_parent_class)->finalize(G_OBJECT(work));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data     = données de nature générique.                      *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                callback = routine de traitements particuliers.              *
*                status   = bilan final à constituer. [OUT]                   *
*                                                                             *
*  Description : Crée une tâche de traitement séquentiel basique.             *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSeqWork *g_seq_work_new(void *data, size_t begin, size_t end, activity_id_t id, seq_work_cb callback)
{
    GSeqWork *result;                       /* Tâche à retourner           */

    result = g_object_new(G_TYPE_SEQ_WORK, NULL);

    result->data = data;

    result->begin = begin;
    result->end = end;

    result->id = id;

    result->type = SWT_SIMPLE;

    result->callback.void_cb = callback;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data     = données de nature générique.                      *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                callback = routine de traitements particuliers.              *
*                status   = bilan final à constituer. [OUT]                   *
*                                                                             *
*  Description : Crée une tâche de traitement séquentiel avec retour booléen. *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSeqWork *g_seq_work_new_boolean(void *data, size_t begin, size_t end, activity_id_t id, seq_work_bool_cb callback, bool *status)
{
    GSeqWork *result;                       /* Tâche à retourner           */

    result = g_object_new(G_TYPE_SEQ_WORK, NULL);

    result->data = data;

    result->begin = begin;
    result->end = end;

    result->id = id;

    result->type = SWT_BOOLEAN;

    result->callback.bool_cb = callback;

    result->status = status;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data     = données de nature générique.                      *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                callback = routine de traitements particuliers.              *
*                status   = bilan final à constituer. [OUT]                   *
*                                                                             *
*  Description : Crée une tâche de traitement séquentiel avec objects.        *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSeqWork *g_seq_work_new_object(void *data, size_t begin, size_t end, activity_id_t id, seq_work_obj_cb callback, bool *status)
{
    GSeqWork *result;                       /* Tâche à retourner           */

    result = g_object_new(G_TYPE_SEQ_WORK, NULL);

    result->data = data;

    result->begin = begin;
    result->end = end;

    result->id = id;

    result->type = SWT_OBJECT;

    result->callback.obj_cb = callback;

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

static void g_seq_work_process(GSeqWork *work, GtkStatusStack *status)
{
    size_t i;                               /* Boucle de parcours          */
    bool state;                             /* Bilan booléen obtenu        */
    GObject *obj;                           /* Object chargé en mémoire    */

    state = true;

    for (i = work->begin; i < work->end && state; i++)
        switch (work->type)
        {
            case SWT_SIMPLE:
                work->callback.void_cb(work->data, i, status, work->id);
                break;

            case SWT_BOOLEAN:
                state = work->callback.bool_cb(work->data, i, status, work->id);
                break;

            case SWT_OBJECT:

                obj = work->callback.obj_cb(work->data, i, status, work->id);

                if (obj != NULL)
                    g_object_unref(obj);
                else
                    state = false;

                break;

        }

    if (work->status != NULL && (work->type == SWT_BOOLEAN || work->type == SWT_OBJECT))
        *(work->status) = (i == work->end && state);

}
