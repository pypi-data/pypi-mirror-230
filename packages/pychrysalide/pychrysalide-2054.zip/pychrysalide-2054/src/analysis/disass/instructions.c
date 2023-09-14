
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instructions.c - étude complémentaire des instructions désassemblées
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "instructions.h"


#include "links.h"
#include "../../glibext/delayed-int.h"



/* Fraction d'instructions à limiter (instance) */
struct _GInstructionsStudy
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GArchProcessor *proc;                   /* Processeurs avec ses instr. */
    GProcContext *ctx;                      /* Suivi du désassemblage      */
    GExeFormat *format;                     /* Format binaire à manipuler  */

    ins_fallback_cb fallback;               /* Routine de traitement finale*/
    size_t begin;                           /* Point de départ du parcours */
    size_t end;                             /* Point d'arrivée exclu       */

    activity_id_t id;                       /* Identifiant pour messages   */

};

/* Fraction d'instructions à limiter (classe) */
struct _GInstructionsStudyClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches d'étude d'instructions. */
static void g_instructions_study_class_init(GInstructionsStudyClass *);

/* Initialise une tâche d'étude d'instructions. */
static void g_instructions_study_init(GInstructionsStudy *);

/* Supprime toutes les références externes. */
static void g_instructions_study_dispose(GInstructionsStudy *);

/* Procède à la libération totale de la mémoire. */
static void g_instructions_study_finalize(GInstructionsStudy *);

/* Assure l'étude des instructions en différé. */
static void g_instructions_study_process(GInstructionsStudy *, GtkStatusStack *);



/* Indique le type défini pour les tâches d'étude d'instructions. */
G_DEFINE_TYPE(GInstructionsStudy, g_instructions_study, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches d'étude d'instructions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_instructions_study_class_init(GInstructionsStudyClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_instructions_study_dispose;
    object->finalize = (GObjectFinalizeFunc)g_instructions_study_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_instructions_study_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une tâche d'étude d'instructions.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_instructions_study_init(GInstructionsStudy *study)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_instructions_study_dispose(GInstructionsStudy *study)
{
    g_clear_object(&study->proc);
    g_clear_object(&study->ctx);
    g_clear_object(&study->format);

    G_OBJECT_CLASS(g_instructions_study_parent_class)->dispose(G_OBJECT(study));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_instructions_study_finalize(GInstructionsStudy *study)
{
    G_OBJECT_CLASS(g_instructions_study_parent_class)->finalize(G_OBJECT(study));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc     = ensemble d'instructions désassemblées.            *
*                ctx      = contexte fourni pour suivre le désassemblage.     *
*                format   = accès aux données du binaire d'origine.           *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                fallback = routine de traitements particuliers.              *
*                                                                             *
*  Description : Crée une tâche d'étude d'instructions différée.              *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GInstructionsStudy *g_instructions_study_new(GArchProcessor *proc, GProcContext *ctx, GExeFormat *format, size_t begin, size_t end, activity_id_t id, ins_fallback_cb fallback)
{
    GInstructionsStudy *result;                /* Tâche à retourner           */

    result = g_object_new(G_TYPE_INSTRUCTIONS_STUDY, NULL);

    result->proc = proc;
    g_object_ref(G_OBJECT(proc));

    result->ctx = ctx;
    g_object_ref(G_OBJECT(ctx));

    result->format = format;
    g_object_ref(G_OBJECT(format));

    result->fallback = fallback;
    result->begin = begin;
    result->end = end;

    result->id = id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study  = étude d'instructions à mener.                       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure l'étude des instructions en différé.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_instructions_study_process(GInstructionsStudy *study, GtkStatusStack *status)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = study->begin; i < study->end; i++)
    {
        study->fallback(study, i);

        gtk_status_stack_update_activity_value(status, study->id, 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = étude d'instructions à mener.                        *
*                index = indice de l'insruction visée.                        *
*                                                                             *
*  Description : Réalise l'appel de type IPH_LINK sur une instruction.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_instructions_study_do_link_operation(GInstructionsStudy *study, size_t index)
{
    GArchInstruction *instr;                /* Instruction en traitement   */

    g_arch_processor_lock(study->proc);

    instr = g_arch_processor_get_instruction(study->proc, index);

    g_arch_processor_unlock(study->proc);

    g_arch_instruction_call_hook(instr, IPH_LINK, study->proc, study->ctx, study->format);

    g_object_unref(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = étude d'instructions à mener.                        *
*                index = indice de l'insruction visée.                        *
*                                                                             *
*  Description : Réalise l'appel de type IPH_POST sur une instruction.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_instructions_study_do_post_operation(GInstructionsStudy *study, size_t index)
{
    GArchInstruction *instr;                /* Instruction en traitement   */

    g_arch_processor_lock(study->proc);

    instr = g_arch_processor_get_instruction(study->proc, index);

    g_arch_processor_unlock(study->proc);

    g_arch_instruction_call_hook(instr, IPH_POST, study->proc, study->ctx, study->format);

    g_object_unref(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = étude d'instructions à mener.                        *
*                index = indice de l'insruction visée.                        *
*                                                                             *
*  Description : Etablit les liens entres les différentes instructions.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_instructions_study_establish_links(GInstructionsStudy *study, size_t index)
{
    GArchInstruction *instr;                /* Instruction en traitement   */
    GArchInstruction *prev;                 /* Instruction précédente      */

    g_arch_processor_lock(study->proc);

    instr = g_arch_processor_get_instruction(study->proc, index);

    g_arch_processor_unlock(study->proc);

    if (index > 0)
    {
        g_arch_processor_lock(study->proc);

        prev = g_arch_processor_get_instruction(study->proc, index - 1);

        g_arch_processor_unlock(study->proc);

        establish_natural_link(instr, prev);

        g_object_unref(G_OBJECT(prev));

    }

    establish_links_for_instruction(instr, G_BIN_FORMAT(study->format), study->proc);

    g_object_unref(G_OBJECT(instr));

}
