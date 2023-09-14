
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hunter.c - recherche de portes vers le noyau
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "hunter.h"


#include <analysis/routine.h>
#include <glibext/delayed-int.h>


#include "db.h"



/* Chasse à l'appel système (instance) */
struct _GGateHunter
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire chargé et concerné  */
    GBinFormat *format;                     /* Format de fichier manipulé  */
    GProcContext *context;                  /* Contexte de désassemblage   */

    size_t begin;                           /* Point de départ du parcours */
    size_t end;                             /* Point d'arrivée exclu       */

    activity_id_t id;                       /* Identifiant pour messages   */

    const hunting_ops *hops;                /* Opérations particulières    */
    sqlite3 *db;                            /* Base de données à manipuler */

};

/* Chasse à l'appel système (classe) */
struct _GGateHunterClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches d'étude de routines. */
static void g_gate_hunter_class_init(GGateHunterClass *);

/* Initialise une tâche d'étude de routines. */
static void g_gate_hunter_init(GGateHunter *);

/* Supprime toutes les références externes. */
static void g_gate_hunter_dispose(GGateHunter *);

/* Procède à la libération totale de la mémoire. */
static void g_gate_hunter_finalize(GGateHunter *);

/* Effectue une recherche d'appels système. */
static void g_gate_hunter_process(GGateHunter *, GtkStatusStack *);



/* Indique le type défini pour les tâches d'étude de routines. */
G_DEFINE_TYPE(GGateHunter, g_gate_hunter, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches d'étude de routines.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gate_hunter_class_init(GGateHunterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_gate_hunter_dispose;
    object->finalize = (GObjectFinalizeFunc)g_gate_hunter_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_gate_hunter_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hunter = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une tâche d'étude de routines.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gate_hunter_init(GGateHunter *hunter)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hunter = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gate_hunter_dispose(GGateHunter *hunter)
{
    g_object_unref(G_OBJECT(hunter->binary));

    g_binary_format_unlock_symbols_rd(hunter->format);
    g_object_unref(G_OBJECT(hunter->format));

    g_object_unref(G_OBJECT(hunter->context));

    G_OBJECT_CLASS(g_gate_hunter_parent_class)->dispose(G_OBJECT(hunter));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hunter = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gate_hunter_finalize(GGateHunter *hunter)
{
    if (hunter->db != NULL)
        close_syscalls_database(hunter->db);

    G_OBJECT_CLASS(g_gate_hunter_parent_class)->finalize(G_OBJECT(hunter));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = binaire dont la définition est à compléter.        *
*                context = contexte de désassemblage.                         *
*                begin   = point de départ du parcours de liste.              *
*                end     = point d'arrivée exclu du parcours.                 *
*                id      = identifiant du message affiché à l'utilisateur.    *
*                hops    = opérations spécifiques à une architecture.         *
*                                                                             *
*  Description : Crée une tâche de recherche de portes différée.              *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGateHunter *g_gate_hunter_new(GLoadedBinary *binary, GProcContext *context, size_t begin, size_t end, activity_id_t id, const hunting_ops *hops)
{
    GGateHunter *result;                /* Tâche à retourner           */

    result = g_object_new(G_TYPE_GATE_HUNTER, NULL);

    result->binary = binary;
    g_object_ref(G_OBJECT(binary));

    result->format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    g_binary_format_lock_symbols_rd(result->format);

    result->context = context;
    g_object_ref(G_OBJECT(context));

    result->begin = begin;
    result->end = end;

    result->id = id;

    result->hops = hops;

    result->db = open_syscalls_database();
    if (result->db == NULL) goto gghn_db_error;

    return result;

 gghn_db_error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hunter = étude de routines à mener.                          *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Effectue une recherche d'appels système.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gate_hunter_process(GGateHunter *hunter, GtkStatusStack *status)
{
    GArchProcessor *proc;                   /* Architecture du binaire     */
    size_t i;                               /* Boucle de parcours #1       */
    GBinSymbol *symbol;                     /* Commodité d'accès           */
    const mrange_t *range;                  /* Couverture d'une routine    */
    instr_iter_t *iter;                     /* Boucle de parcours #2       */
    GArchInstruction *instr;                /* Instruction analysée        */
    tracked_path *exec;                     /* Chemin d'exécution à suivre */
    unsigned int nr;                        /* Numéro d'appel système      */
    bool ret;                               /* Bilan d'un appel            */
    syscall_info_t *info;                   /* Information sur l'appel     */
    size_t loop;                            /* Quantité de boucles en vue  */
    size_t k;                               /* Boucle de parcours #3       */
    comment_writer *writer;                 /* Ecriture de commentaires    */

    proc = g_loaded_binary_get_processor(hunter->binary);

    for (i = hunter->begin; i < hunter->end; i++)
    {
        symbol = g_binary_format_get_symbol(hunter->format, i);

        if (!G_IS_BIN_ROUTINE(symbol))
            goto gghp_next;

        range = g_binary_symbol_get_range(symbol);

        iter = g_arch_processor_get_iter_from_address(proc, get_mrange_addr(range));

        if (iter != NULL)
        {
            restrict_instruction_iterator(iter, range);

            for (instr = get_instruction_iterator_current(iter);
                 instr != NULL;
                 instr = get_instruction_iterator_next(iter))
            {
                if (hunter->hops->is_syscall(instr))
                {
                    exec = create_register_tracker(iter);

                    ret = hunter->hops->resolve_nr(exec, proc, hunter->hops, &nr);
                    if (!ret) goto unknown_syscall;

                    info = extract_from_syscalls_database(hunter->db, hunter->hops->arch, nr);
                    if (info == NULL) goto unknown_syscall;

                    loop = count_register_tracker_stacks(exec);

                    for (k = 0; k < loop; k++)
                    {
                        ret = hunter->hops->look_for_args(exec, k, info->argc);
                        if (!ret) goto unknown_syscall;

                        look_for_registers(exec, k, proc, hunter->hops);

                    }

                    writer = create_comment_writer();

                    loop = count_register_tracker_stacks(exec);

                    for (k = 0; k < loop; k++)
                        hunter->hops->comment(exec, k, info, writer);

                    write_all_comments(writer, G_PRELOAD_INFO(hunter->context));

                    delete_comment_writer(writer);

 unknown_syscall:

                    delete_register_tracker(exec);

                }

                g_object_unref(G_OBJECT(instr));

            }

            delete_instruction_iterator(iter);

        }

 gghp_next:

        gtk_status_stack_update_activity_value(status, hunter->id, 1);

        g_object_unref(G_OBJECT(symbol));

    }

    g_object_unref(G_OBJECT(proc));

}
