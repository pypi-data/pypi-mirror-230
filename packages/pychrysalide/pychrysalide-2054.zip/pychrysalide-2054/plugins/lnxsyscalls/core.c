
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - greffon détaillant les appels système
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


#include "core.h"


#include <i18n.h>


#include <core/global.h>
#include <core/nproc.h>
#include <plugins/self.h>


#include "db.h"
#include "hops_armv7.h"
#include "hunter.h"



DEFINE_CHRYSALIDE_PLUGIN("LinuxSyscalls", "Describes each Linux system call with its arguments",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE(""),
                         NO_REQ, AL(PGA_PLUGIN_INIT, PGA_DISASSEMBLY_ENDED));



/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du chargement du greffon.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_init(GPluginModule *plugin)
{
    bool result;                            /* Bilan à retourner           */
    sqlite3 *db;                            /* Base de données présente    */

    db = open_syscalls_database();

    if (db != NULL)
    {
        introduce_syscalls_database(db);

        close_syscalls_database(db);

        result = true;

    }

    else
        result = false;

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                binary  = binaire dont le contenu est en cours de traitement.*
*                status  = barre de statut à tenir informée.                  *
*                context = contexte de désassemblage.                         *
*                                                                             *
*  Description : Exécute une action pendant un désassemblage de binaire.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT void chrysalide_plugin_process_disassembly_event(const GPluginModule *plugin, PluginAction action, GLoadedBinary *binary, GtkStatusStack *status, GProcContext *context)
{
    GBinFormat *format;                     /* Format du binaire chargé    */
    const char *arch;                       /* Architecture d'exécution    */
    const hunting_ops *hops;                /* Opérations particulières    */
    size_t sym_count;                       /* Nombre de ces symboles      */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    size_t run_size;                        /* Volume réparti par exécution*/
    activity_id_t id;                       /* Identifiant de progression  */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    wgroup_id_t gid;                        /* Identifiant pour les tâches */
    guint i;                                /* Boucle de parcours          */
    size_t begin;                           /* Début de bloc de traitement */
    size_t end;                             /* Fin d'un bloc de traitement */
    GGateHunter *hunter;                    /* Tâche d'étude à programmer  */

    format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    if (g_binary_format_has_flag(format, FFL_RUN_IN_KERNEL_SPACE))
        goto pbd_exit;

    arch = g_exe_format_get_target_machine(G_EXE_FORMAT(format));

    if (0 && strcmp(arch, "armv7") == 0)
        hops = get_armv7_hunting_ops();

    else
    {
        log_plugin_simple_message(LMT_WARNING, _("No suitable backend to track syscalls!"));
        goto pbd_exit;
    }

    g_binary_format_lock_symbols_rd(format);

    sym_count = g_binary_format_count_symbols(format);

    run_size = compute_run_size(sym_count, &runs_count);

    id = gtk_status_stack_add_activity(status, _("Looking for Linux syscalls..."), sym_count);

    queue = get_work_queue();

    gid = g_work_queue_define_work_group(queue);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = sym_count;
        else
            end = begin + run_size;

        hunter = g_gate_hunter_new(binary, context, begin, end, id, hops);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(hunter), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    g_work_queue_delete_work_group(queue, gid);

    gtk_status_stack_remove_activity(status, id);

    g_binary_format_unlock_symbols_rd(format);

 pbd_exit:

    g_object_unref(G_OBJECT(format));

}
