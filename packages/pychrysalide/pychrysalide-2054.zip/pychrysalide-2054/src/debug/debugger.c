
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debugger.c - gestion des différents débogueurs
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "debugger.h"


#include <assert.h>
#include <inttypes.h>
#include <malloc.h>
#include <stdlib.h>


#include <i18n.h>


#include "debugger-int.h"
#include "../common/sort.h"
#include "../core/logs.h"
#include "../glibext/chrysamarshal.h"
#include "../plugins/pglist.h"



/* ---------------------------- TRONC COMMUN DE DEBOGAGE ---------------------------- */


/* Initialise la classe de base des débogueurs. */
static void g_binary_debugger_class_init(GBinaryDebuggerClass *);

/* Initialise une instance de base d'un débogueur. */
static void g_binary_debugger_init(GBinaryDebugger *);

/* Supprime toutes les références externes. */
static void g_binary_debugger_dispose(GBinaryDebugger *);

/* Procède à la libération totale de la mémoire. */
static void g_binary_debugger_finalize(GBinaryDebugger *);



/* --------------------------- GESTION DES POINTS D'ARRET --------------------------- */


/* Active un point d'arrêt à un emplacement de mémoire donné. */
static bool g_binary_debugger_insert_memory_breakpoint(GBinaryDebugger *, virt_t, RawBpOrigin, dbg_thread_id_t, virt_t);

/* Désactive un point d'arrêt à un emplacement de mémoire donné. */
static bool g_binary_debugger_remove_memory_breakpoint(GBinaryDebugger *, virt_t);

/* Sème des points d'arrêt sur les instructions suivantes. */
static bool g_binary_debugger_spread_breakpoints(GBinaryDebugger *, dbg_thread_id_t, virt_t, RawBpOrigin, bool);

/* Retire tous les points d'arrêt issus d'un adresse. */
static void g_binary_debugger_remove_same_breakpoints(GBinaryDebugger *, dbg_thread_id_t, virt_t, RawBpOrigin);

/* Met à jour les points d'arrêt suite à un arrêt. */
static bool g_binary_debugger_update_breakpoints_on_stop(GBinaryDebugger *, dbg_thread_id_t, virt_t);



/* ---------------------------------------------------------------------------------- */
/*                              TRONC COMMUN DE DEBOGAGE                              */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une ligne de représentation. */
G_DEFINE_TYPE(GBinaryDebugger, g_binary_debugger, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe de base des débogueurs.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_debugger_class_init(GBinaryDebuggerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_binary_debugger_dispose;
    object->finalize = (GObjectFinalizeFunc)g_binary_debugger_finalize;

    g_signal_new("signaled",
                 G_TYPE_BINARY_DEBUGGER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinaryDebuggerClass, signaled),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__INT,
                 G_TYPE_NONE, 1, G_TYPE_INT);

    g_signal_new("exited",
                 G_TYPE_BINARY_DEBUGGER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinaryDebuggerClass, exited),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__INT_INT,
                 G_TYPE_NONE, 2, G_TYPE_INT, G_TYPE_INT);

    g_signal_new("terminated",
                 G_TYPE_BINARY_DEBUGGER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinaryDebuggerClass, terminated),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__INT_INT,
                 G_TYPE_NONE, 2, G_TYPE_INT, G_TYPE_INT);

    g_signal_new("stopped",
                 G_TYPE_BINARY_DEBUGGER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinaryDebuggerClass, stopped),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__UINT64,
                 G_TYPE_NONE, 1, G_TYPE_UINT64);



    g_signal_new("halted",
                 G_TYPE_BINARY_DEBUGGER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinaryDebuggerClass, debugger_halted),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__INT_UINT64_INT,
                 G_TYPE_NONE, 3, G_TYPE_INT, G_TYPE_UINT64, G_TYPE_INT);





    g_signal_new("mem-bp-handled",
                 G_TYPE_BINARY_DEBUGGER,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBinaryDebuggerClass, mem_bp_handled),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__INT_UINT64_INT,
                 G_TYPE_NONE, 2, G_TYPE_BOOLEAN, G_TYPE_UINT64);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une instance de base d'un débogueur.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_debugger_init(GBinaryDebugger *debugger)
{
    g_rw_lock_init(&debugger->bp_lock);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_debugger_dispose(GBinaryDebugger *debugger)
{
    g_object_unref(G_OBJECT(debugger->binary));

    g_rw_lock_clear(&debugger->bp_lock);

    G_OBJECT_CLASS(g_binary_debugger_parent_class)->dispose(G_OBJECT(debugger));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_debugger_finalize(GBinaryDebugger *debugger)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < debugger->bp_count; i++)
        fini_raw_breakpoint(debugger->bpoints[i]);

    if (debugger->bpoints != NULL)
        free(debugger->bpoints);

    G_OBJECT_CLASS(g_binary_debugger_parent_class)->finalize(G_OBJECT(debugger));

}





/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                                                                             *
*  Description : Démarre une procédure de débogage.                           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_attach(GBinaryDebugger *debugger)
{
    bool result;                            /* Bilan à retourner           */
    GPluginModule **pglist;                 /* Liste de greffons           */
    size_t pgcount;                         /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */

    if (debugger->attach == NULL) result = true;
    else result = debugger->attach(debugger);

    pgcount = 0;
    pglist = NULL;//get_all_plugins_for_action(PGA_DEBUGGER_ATTACH, &pgcount);

    if (pgcount > 0)
    {
        /*
        for (i = 0; i < pgcount; i++)
            g_plugin_module_handle_debugger(pglist[i], debugger, PGA_DEBUGGER_ATTACH);
        */

        free(pglist);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                                                                             *
*  Description : Démarre une procédure de débogage.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_debugger_run(GBinaryDebugger *debugger)
{
    debugger->run(debugger);

}




/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                                                                             *
*  Description : Tue une procédure de débogage.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_debugger_kill(GBinaryDebugger *debugger)
{
    debugger->kill(debugger);

}











/* ------------------- MANIPULATION DES DIFFERENTS THREADS ACTIFS ------------------- */



/* ---------------------------------------------------------------------------------- */
/*                     MANIPULATION DES DIFFERENTS THREADS ACTIFS                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = descriptions à supprimer de la mémoire.              *
*                count = taille de cette liste.                               *
*                                                                             *
*  Description : Libère la mémoire d'une liste de threads actifs.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_dbg_thread_desc(dbg_thread_desc *list, size_t count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < count; i++)
        free(list[i].name);

    if (list != NULL)
        free(list);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = instance du module de débogage chargé.            *
*                names    = désignations de tous les threads ou NULL. [OUT]   *
*                count    = nombre de threads actifs. [OUT]                   *
*                                                                             *
*  Description : Fournit les identifiants de tous les threads actifs.         *
*                                                                             *
*  Retour      : Liste des threads décomptés, à libérer de la mémoire ensuite.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dbg_thread_desc *g_binary_debugger_list_all_threads(GBinaryDebugger *debugger, size_t *count)
{
    dbg_thread_desc *result;                /* Liste à retourner           */

    *count = 0;

    result = G_BINARY_DEBUGGER_GET_CLASS(debugger)->all_threads(debugger, count);

    if (result != NULL)
    {
        int cmp_dbg_thread_desc(const dbg_thread_desc *a, const dbg_thread_desc *b)
        {
            int status;                     /* Bilan à retourner           */

            if (a->id < b->id)
                status = -1;

            if (a->id > b->id)
                status = 1;

            else
                status = -1;

            return status;

        }

        qsort(result, *count, sizeof(dbg_thread_desc), (__compar_fn_t)cmp_dbg_thread_desc);

    }

    return result;

}










/* ---------------------------------------------------------------------------------- */
/*                             ENTREES / SORTIES BASIQUES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir consulter.         *
*                value    = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Lit une valeur de 8 bits à une adresse arbitraire.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_memory_u8(GBinaryDebugger *debugger, virt_t addr, uint8_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_mem(debugger, addr, 8, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir consulter.         *
*                value    = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Lit une valeur de 16 bits à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_memory_u16(GBinaryDebugger *debugger, virt_t addr, uint16_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_mem(debugger, addr, 16, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir consulter.         *
*                value    = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Lit une valeur de 32 bits à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_memory_u32(GBinaryDebugger *debugger, virt_t addr, uint32_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_mem(debugger, addr, 32, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir consulter.         *
*                value    = emplacement de la valeur lue à conserver. [OUT]   *
*                                                                             *
*  Description : Lit une valeur de 64 bits à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_memory_u64(GBinaryDebugger *debugger, virt_t addr, uint64_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_mem(debugger, addr, 64, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir consulter.         *
*                value    = emplacement de la valeur lue à conserver. [OUT]   *
*                len      = taille attendue de la valeur en octets.           *
*                                                                             *
*  Description : Lit une valeur de taille quelconque à une adresse arbitraire.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_memory_data(GBinaryDebugger *debugger, virt_t addr, uint8_t *value, size_t len)
{
    bool result;                            /* Bilan à retourner           */
    size_t iter;                            /* Tête de lecture / écriture  */
    size_t remaining;                       /* Quantité restant à replacer */

    result = true;

    iter = 0;
    remaining = len;

    while (result && remaining > 0)
    {
        if (remaining >= 8)
        {
            result = g_binary_debugger_read_memory_u64(debugger, addr + iter, (uint64_t *)&value[iter]);

            iter += 8;
            remaining -= 8;

        }

        else if (remaining >= 4)
        {
            result = g_binary_debugger_read_memory_u32(debugger, addr + iter, (uint32_t *)(&value[iter]));

            iter += 4;
            remaining -= 4;

        }

        else if (remaining >= 2)
        {
            result = g_binary_debugger_read_memory_u16(debugger, addr + iter, (uint16_t *)&value[iter]);

            iter += 2;
            remaining -= 2;

        }

        else if (remaining >= 1)
        {
            result = g_binary_debugger_read_memory_u8(debugger, addr + iter, (uint8_t *)&value[iter]);

            iter += 1;
            remaining -= 1;

        }

        else
            assert(false);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir modifier.          *
*                value    = emplacement de la valeur à inscrire.              *
*                                                                             *
*  Description : Ecrit une valeur de 8 bits à une adresse arbitraire.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_memory_u8(GBinaryDebugger *debugger, virt_t addr, const uint8_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_mem(debugger, addr, 8, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir modifier.          *
*                value    = emplacement de la valeur à inscrire.              *
*                                                                             *
*  Description : Ecrit une valeur de 16 bits à une adresse arbitraire.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_memory_u16(GBinaryDebugger *debugger, virt_t addr, const uint16_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_mem(debugger, addr, 16, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir modifier.          *
*                value    = emplacement de la valeur à inscrire.              *
*                                                                             *
*  Description : Ecrit une valeur de 32 bits à une adresse arbitraire.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_memory_u32(GBinaryDebugger *debugger, virt_t addr, const uint32_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_mem(debugger, addr, 32, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir modifier.          *
*                value    = emplacement de la valeur à inscrire.              *
*                                                                             *
*  Description : Ecrit une valeur de 64 bits à une adresse arbitraire.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_memory_u64(GBinaryDebugger *debugger, virt_t addr, const uint64_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_mem(debugger, addr, 64, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                addr     = emplacement en mémoire à venir modifier.          *
*                value    = emplacement de la valeur à incrire.               *
*                len      = taille de la valeur fournie en octets.            *
*                                                                             *
*  Description : Ecrit une valeur de taille quelconque à une adresse donnée.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_memory_data(GBinaryDebugger *debugger, virt_t addr, const uint8_t *value, size_t len)
{
    bool result;                            /* Bilan à retourner           */
    size_t iter;                            /* Tête de lecture / écriture  */
    size_t remaining;                       /* Quantité restant à replacer */

    result = true;

    iter = 0;
    remaining = len;

    while (result && remaining > 0)
    {
        if (remaining >= 8)
        {
            result = g_binary_debugger_write_memory_u64(debugger, addr + iter, (uint64_t *)&value[iter]);

            iter += 8;
            remaining -= 8;

        }

        else if (remaining >= 4)
        {
            result = g_binary_debugger_write_memory_u32(debugger, addr + iter, (uint32_t *)&value[iter]);

            iter += 4;
            remaining -= 4;

        }

        else if (remaining >= 2)
        {
            result = g_binary_debugger_write_memory_u16(debugger, addr + iter, (uint16_t *)&value[iter]);

            iter += 2;
            remaining -= 2;

        }

        else if (remaining >= 1)
        {
            result = g_binary_debugger_write_memory_u8(debugger, addr + iter, (uint8_t *)&value[iter]);

            iter += 1;
            remaining -= 1;

        }

        else
            assert(false);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                group    = éventuel groupe de registres ciblé ou NULL.       *
*                count    = nombre d'éléments dans la liste de noms. [OUT]    *
*                                                                             *
*  Description : Liste l'ensemble des registres appartenant à un groupe.      *
*                                                                             *
*  Retour      : Liste de noms à libérer de la mémoire après utilisation.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char **g_binary_debugger_get_register_names(const GBinaryDebugger *debugger, const char *group, size_t *count)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->get_reg_names(debugger, group, count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                name     = désignation du registre visé.                     *
*                                                                             *
*  Description : Indique la taille associée à un registre donné.              *
*                                                                             *
*  Retour      : Taille en bits, ou 0 si le registre n'a pas été trouvé.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int g_binary_debugger_get_register_size(const GBinaryDebugger *debugger, const char *name)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->get_reg_size(debugger, name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur lue à conserver. [OUT]  *
*                                                                             *
*  Description : Lit une valeur de 8 bits à partir d'un registre.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_register_u8(GBinaryDebugger *debugger, const char *reg, uint8_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_reg(debugger, reg, 8, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur lue à conserver. [OUT]  *
*                                                                             *
*  Description : Lit une valeur de 16 bits à partir d'un registre.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_register_u16(GBinaryDebugger *debugger, const char *reg, uint16_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_reg(debugger, reg, 16, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur lue à conserver. [OUT]  *
*                                                                             *
*  Description : Lit une valeur de 32 bits à partir d'un registre.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_register_u32(GBinaryDebugger *debugger, const char *reg, uint32_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_reg(debugger, reg, 32, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur lue à conserver. [OUT]  *
*                                                                             *
*  Description : Lit une valeur de 64 bits à partir d'un registre.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_read_register_u64(GBinaryDebugger *debugger, const char *reg, uint64_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->read_reg(debugger, reg, 64, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur à écrire.               *
*                                                                             *
*  Description : Ecrit une valeur de 8 bits dans un registre.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_register_u8(GBinaryDebugger *debugger, const char *reg, const uint8_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_reg(debugger, reg, 8, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur à écrire.               *
*                                                                             *
*  Description : Ecrit une valeur de 16 bits dans un registre.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_register_u16(GBinaryDebugger *debugger, const char *reg, const uint16_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_reg(debugger, reg, 16, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur à écrire.               *
*                                                                             *
*  Description : Ecrit une valeur de 32 bits dans un registre.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_register_u32(GBinaryDebugger *debugger, const char *reg, const uint32_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_reg(debugger, reg, 32, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler.                            *
*                reg      = désignation humaine du register à consulter.      *
*                value    =  emplacement de la valeur à écrire.               *
*                                                                             *
*  Description : Ecrit une valeur de 64 bits dans un registre.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_write_register_u64(GBinaryDebugger *debugger, const char *reg, const uint64_t *value)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->write_reg(debugger, reg, 64, value);

}



/* ---------------------------------------------------------------------------------- */
/*                           MANIPULATION DE L'ETAT COURANT                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                pc       = adresse de l'instruction courante. [OUT]          *
*                                                                             *
*  Description : Détermine le point d'exécution courant.                      *
*                                                                             *
*  Retour      : Bilan de la récupération.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_get_current_pc(GBinaryDebugger *debugger, virt_t *pc)
{
    bool result;                            /* Bilan à retourner           */

    result = G_BINARY_DEBUGGER_GET_CLASS(debugger)->get_current_pc(debugger, pc);

    if (!result)
        log_variadic_message(LMT_WARNING, "Unable to get the current PC!");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                pc       = adresse de l'instruction de retour d'appel. [OUT] *
*                                                                             *
*  Description : Détermine l'adresse du premier retour d'appel.               *
*                                                                             *
*  Retour      : Bilan de la récupération.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_get_return_pc(GBinaryDebugger *debugger, virt_t *pc)
{
    bool result;                            /* Bilan à retourner           */
    virt_t *callstack;                      /* Pile d'appels courante      */
    size_t size;                            /* Hauteur de cette pile       */

    result = g_binary_debugger_get_call_stack(debugger, &callstack, &size);

    if (result && size > 0)
        *pc = callstack[size - 1];

    if (callstack != NULL)
        free(callstack);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à consulter.                            *
*                over     = indique si les appels doivent être sautés ou non. *
*                count    = nombre d'adresses identifiées.                    *
*                                                                             *
*  Description : Détermine les prochaines probables instructions exécutées.   *
*                                                                             *
*  Retour      : Liste d'adresses à libérer de la mémoire après usage.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

virt_t *g_binary_debugger_get_next_pcs(GBinaryDebugger *debugger, virt_t pc, bool over, size_t *count)
{
    virt_t *result;                         /* Liste à retourner           */
    GArchProcessor *proc;                   /* Processeur lié au binaire   */
    vmpa2t addr;                            /* Localisation à cibler       */
    const instr_iter_t *iter;               /* Parcours local d'adresses   */
    GArchInstruction *instr;                /* Instruction correspondante  */
    virt_t ret;                             /* Adresse de retour d'appel   */
    size_t dcount;                          /* Nombre de liens de dest.    */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dest;               /* Instr. visée par une autre  */
    const mrange_t *range;                  /* Emplacement d'instruction   */

    result = NULL;
    *count = 0;

    proc = g_loaded_binary_get_processor(debugger->binary);

    init_vmpa(&addr, VMPA_NO_PHYSICAL, pc);
    iter = g_arch_processor_get_iter_from_address(proc, &addr);

    if (iter != NULL)
    {
        instr = get_instruction_iterator_current(iter);

        /* Si l'instruction est un retour à l'appelant */
        if (g_arch_instruction_get_flags(instr) & AIF_RETURN_POINT)
        {
            if (g_binary_debugger_get_return_pc(debugger, &ret))
            {
                *count = 1;
                result = (virt_t *)malloc(sizeof(virt_t));

                result[0] = ret;

            }

        }

        /* Sinon on se penche sur ses destinations */
        else
        {
            g_arch_instruction_lock_dest(instr);

            dcount = g_arch_instruction_count_destinations(instr);

            for (i = 0; i < dcount; i++)
            {
                dest = g_arch_instruction_get_destination(instr, i);

                switch (dest->type)
                {
                    case ILT_EXEC_FLOW:
                    case ILT_JUMP:
                    case ILT_CASE_JUMP:
                    case ILT_JUMP_IF_TRUE:
                    case ILT_JUMP_IF_FALSE:
                    case ILT_LOOP:

                        (*count)++;
                        result = (virt_t *)realloc(result, *count * sizeof(virt_t));

                        range = g_arch_instruction_get_range(dest->linked);

                        result[*count - 1] = get_virt_addr(get_mrange_addr(range));
                        break;

                    case ILT_CALL:

                        if (!over)
                        {
                            (*count)++;
                            result = (virt_t *)realloc(result, *count * sizeof(virt_t));

                            range = g_arch_instruction_get_range(dest->linked);

                            result[*count - 1] = get_virt_addr(get_mrange_addr(range));

                        }

                        break;

                    default:
                        break;

                }

                unref_instr_link(dest);

            }

            g_arch_instruction_unlock_dest(instr);

            /* Si tout ça ne donne rien, on se rabat sur l'instruction suivante par défaut */
            if (*count == 0)
            {
                g_object_unref(G_OBJECT(instr));

                instr = get_instruction_iterator_next(iter);

                if (instr != NULL)
                {
                    *count = 1;
                    result = (virt_t *)malloc(sizeof(virt_t));

                    range = g_arch_instruction_get_range(instr);

                    result[0] = get_virt_addr(get_mrange_addr(range));

                }

            }

        }

        if (instr != NULL)
            g_object_unref(G_OBJECT(instr));

        delete_instruction_iterator(iter);

    }

    g_object_unref(G_OBJECT(proc));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger  = débogueur à consulter.                           *
*                callstack = pile d'appels reconstituée. [OUT]                *
*                size      = taille de cette pile. [OUT]                      *
*                                                                             *
*  Description : Remonte la pile d'appels jusqu'au point courant.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_get_call_stack(GBinaryDebugger *debugger, virt_t **callstack, size_t *size)
{
    bool result;                            /* Bilan à retourner           */

    *callstack = NULL;
    *size = 0;

    result = G_BINARY_DEBUGGER_GET_CLASS(debugger)->get_call_stack(debugger, callstack, size);

    if (!result)
    {
        if (*callstack != NULL)
            free(*callstack);

        *callstack = NULL;
        *size = 0;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                pc       = adresse de l'instruction courante.                *
*                                                                             *
*  Description : Réagit à un arrêt du flot d'exécution.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void on_binary_debugger_stopped(GBinaryDebugger *debugger, virt_t pc)
{
    pid_t tid;                              /* Identifiant du thread       */
    bool auto_resume;                       /* Poursuite automatique ?     */

    tid = 1;    // FIXME

    auto_resume = g_binary_debugger_update_breakpoints_on_stop(debugger, tid, pc);

    if (!auto_resume)
        g_signal_emit_by_name(debugger, "stopped", pc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                pid      = éventuel identifiant de processus concerné ou -1. *
*                                                                             *
*  Description : Réagit à la fin de l'opération de débogage.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void on_binary_debugger_finished(GBinaryDebugger *debugger, pid_t pid)
{

    /* TODO : libérer de la mémoire tous les BP */

}



/* ---------------------------------------------------------------------------------- */
/*                             GESTION DES POINTS D'ARRET                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                addr     = emplacement du point mémoire à traiter.           *
*                origin   = origine de la création du point d'arrêt.          *
*                tid      = identifiant du thread concerné.                   *
*                previous = éventuelle adresse précédent celle du point.      *
*                                                                             *
*  Description : Active un point d'arrêt à un emplacement de mémoire donné.   *
*                                                                             *
*  Retour      : true si la demande a été prise en compte, false sinon.       *
*                                                                             *
*  Remarques   : L'accès à la liste doit être placée sous la protection de    *
*                l'appelant.                                                  *
*                                                                             *
******************************************************************************/

static bool g_binary_debugger_insert_memory_breakpoint(GBinaryDebugger *debugger, virt_t addr, RawBpOrigin origin, dbg_thread_id_t tid, virt_t previous)
{
    bool result;                            /* Bilan à retourner           */
    size_t index;                           /* Indice de ce point d'arrêt  */
    bool found;                             /* Présence d'un point d'arrêt */
    raw_breakpoint *bp;                     /* Point d'arrêt à constituer  */

    result = false;

    found = bsearch_index(&addr, debugger->bpoints, debugger->bp_count, sizeof(raw_breakpoint *),
                          (__compar_fn_t)compare_raw_breakpoint_with_addr, &index);

    if (found)
    {
        bp = debugger->bpoints[index];
        result = true;
    }

    else
    {
        bp = G_BINARY_DEBUGGER_GET_CLASS(debugger)->enable_bp(debugger, addr);

        if (bp != NULL)
        {
            debugger->bpoints = (raw_breakpoint **)qinsert(debugger->bpoints, &debugger->bp_count,
                                                           sizeof(raw_breakpoint *),
                                                           (__compar_fn_t)compare_raw_breakpoints, &bp);
            result = true;
        }

    }

    if (result)
        set_raw_breakpoint_origin(bp, origin, tid, previous);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                index    = indice du point à supprimer.                      *
*                                                                             *
*  Description : Désactive un point d'arrêt à un emplacement de mémoire donné.*
*                                                                             *
*  Retour      : true si la demande a été prise en compte, false sinon.       *
*                                                                             *
*  Remarques   : L'accès à la liste doit être placée sous la protection de    *
*                l'appelant.                                                  *
*                                                                             *
******************************************************************************/

static bool g_binary_debugger_remove_memory_breakpoint(GBinaryDebugger *debugger, size_t index)
{
    bool result;                            /* Bilan à retourner           */
    raw_breakpoint *bp;                     /* Point d'arrêt à manipuler   */

    result = false;

    assert(index < debugger->bp_count);

    bp = debugger->bpoints[index];

    result = G_BINARY_DEBUGGER_GET_CLASS(debugger)->disable_bp(debugger, bp);

    if (result)
    {
        debugger->bpoints = (raw_breakpoint **)_qdelete(debugger->bpoints, &debugger->bp_count,
                                                        sizeof(raw_breakpoint *), index);

        fini_raw_breakpoint(bp);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                tid      = identifiant du thread concerné.                   *
*                pc       = adresse de l'instruction courante.                *
*                type     = type de point d'arrêt à insérer.                  *
*                over     = indique si les appels doivent être sautés ou non. *
*                                                                             *
*  Description : Sème des points d'arrêt sur les instructions suivantes.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_debugger_spread_breakpoints(GBinaryDebugger *debugger, dbg_thread_id_t tid, virt_t pc, RawBpOrigin type, bool over)
{
    bool result;                            /* Bilan à retourner           */
    virt_t *next_list;                      /* Liste de points d'arrêts    */
    size_t next_count;                      /* Taille de cette liste       */
    GArchProcessor *proc;                   /* Processeur lié au binaire   */
    size_t i;                               /* Boucle de parcours          */
    vmpa2t addr;                            /* Format d'adresse complet    */
    GArchInstruction *instr;                /* Instruction ciblée          */
    bool valid;                             /* Point d'arrêt pertinent ?   */
    const char *encoding;                   /* Encodage de l'instruction   */

    result = true;

    next_list = g_binary_debugger_get_next_pcs(debugger, pc, over, &next_count);

    if (next_count == 0)
        log_variadic_message(LMT_WARNING, "No instruction found to break after 0x%" PRIx64, pc);

    proc = g_loaded_binary_get_processor(debugger->binary);

    /**
     * Le verrou sur la liste des points est normalement déjà posé.
     */

    for (i = 0; i < next_count && result; i++)
    {
        /**
         * Des données peuvent suivre du code (typiquement en ARM).
         * On réalise une validation minimale au préalable donc.
         */

        init_vmpa(&addr, VMPA_NO_PHYSICAL, next_list[i]);
        instr = g_arch_processor_find_instr_by_address(proc, &addr);

        if (instr == NULL)
            valid = false;

        else
        {
            encoding = g_arch_instruction_get_encoding(instr);

            valid = strcmp(encoding, _("String")) != 0
                    && strcmp(encoding, _("Raw")) != 0
                    && strcmp(encoding, _("Undefined")) != 0;

            g_object_unref(G_OBJECT(instr));

        }

        if (valid)
            result = g_binary_debugger_insert_memory_breakpoint(debugger, next_list[i], type, tid, pc);

    }

    if (next_list != NULL)
        free(next_list);

    g_object_unref(G_OBJECT(proc));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                tid      = identifiant du thread concerné.                   *
*                prev     = adresse d'instruction qui a conduit à des poses.  *
*                type     = type de point d'arrêt à insérer.                  *
*                                                                             *
*  Description : Retire tous les points d'arrêt issus d'un adresse.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_debugger_remove_same_breakpoints(GBinaryDebugger *debugger, dbg_thread_id_t tid, virt_t prev, RawBpOrigin type)
{
    size_t i;                               /* Boucle de parcours          */
    raw_breakpoint *bp;                     /* Confort de l'accès rapide   */

    /**
     * Le verrou sur la liste des points est normalement déjà posé.
     */

    for (i = 0; i < debugger->bp_count; i++)
    {
        bp = debugger->bpoints[i];

        if (has_raw_breakpoint_previous_address(bp, type, tid, prev))
            unset_raw_breakpoint_origin(bp, type, tid);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                tid      = identifiant du thread concerné.                   *
*                pc       = adresse de l'instruction courante.                *
*                                                                             *
*  Description : Met à jour les points d'arrêt suite à un arrêt.              *
*                                                                             *
*  Retour      : true si l'exécution a été relancée automatiquement.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_debugger_update_breakpoints_on_stop(GBinaryDebugger *debugger, dbg_thread_id_t tid, virt_t pc)
{
    bool result;                            /* Indication à faire remonter */
    size_t index;                           /* Indice de ce point d'arrêt  */
    bool found;                             /* Présence d'un point d'arrêt */
    raw_breakpoint *bp;                     /* Confort de l'accès rapide   */
    virt_t previous;                        /* Adresse d'origine           */
    bool status;                            /* Bilan d'un retrait          */
    size_t i;                               /* Boucle de parcours          */
    virt_t addr;                            /* Localisation d'un point     */

    result = false;

    g_rw_lock_writer_lock(&debugger->bp_lock);

    found = bsearch_index(&pc, debugger->bpoints, debugger->bp_count, sizeof(raw_breakpoint *),
                          (__compar_fn_t)compare_raw_breakpoint_with_addr, &index);

    if (found)
    {
        bp = debugger->bpoints[index];

        /* S'il s'agissait d'un point d'arrêt à usage interne */
        if (has_raw_breakpoint_origin(bp, RBO_INTERNAL, tid))
        {
            previous = get_raw_breakpoint_prev_addr(bp);
            assert(previous != VMPA_NO_VIRTUAL);

            g_binary_debugger_remove_same_breakpoints(debugger, tid, previous, RBO_INTERNAL);

            assert(!has_raw_breakpoint_origin(bp, RBO_INTERNAL, tid));

            result = true;

        }

        /* S'il s'agissait d'un arrêt demandé par l'utilisateur */
        if (has_raw_breakpoint_origin(bp, RBO_USER, tid))
        {
            status = G_BINARY_DEBUGGER_GET_CLASS(debugger)->disable_bp(debugger, bp);

            if (!status)
                log_variadic_message(LMT_ERROR, "Error while removing the breakpoint at 0x%" PRIx64, pc);

            g_binary_debugger_spread_breakpoints(debugger, tid, pc, RBO_INTERNAL, false);

            result = false;

        }

        /* S'il s'agissait d'une progression pas à pas */
        if (has_raw_breakpoint_origin(bp, RBO_STEP, tid))
        {
            previous = get_raw_breakpoint_prev_addr(bp);
            assert(previous != VMPA_NO_VIRTUAL);

            g_binary_debugger_remove_same_breakpoints(debugger, tid, previous, RBO_STEP);

            assert(!has_raw_breakpoint_origin(bp, RBO_STEP, tid));

            result = false;

        }

        /* En conclusion, on supprime les points inutiles */
        for (i = 0; i < debugger->bp_count; )
        {
            bp = debugger->bpoints[i];

            if (is_breakpoint_useless(bp))
            {
                status = g_binary_debugger_remove_memory_breakpoint(debugger, i);

                if (!status)
                {
                    addr = get_raw_breakpoint_addr(bp);
                    log_variadic_message(LMT_ERROR, "Error while removing the breakpoint at 0x%" PRIx64, addr);
                    i++;
                }

            }

            else i++;

        }

    }

    g_rw_lock_writer_unlock(&debugger->bp_lock);

    if (result)
        G_BINARY_DEBUGGER_GET_CLASS(debugger)->resume(debugger);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                addr     = emplacement du point mémoire à traiter.           *
*                                                                             *
*  Description : Ajoute un point d'arrêt basique en mémoire.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_add_memory_breakpoint(GBinaryDebugger *debugger, virt_t addr)
{
    bool result;                            /* Bilan à retourner           */
    dbg_thread_id_t tid;                    /* Identifiant de thread       */

    tid = 1;/// FIXME

    g_rw_lock_writer_lock(&debugger->bp_lock);

    result = g_binary_debugger_insert_memory_breakpoint(debugger, addr, RBO_USER, tid, VMPA_NO_VIRTUAL);

    g_rw_lock_writer_unlock(&debugger->bp_lock);

    if (result)
        g_signal_emit_by_name(debugger, "mem-bp-handled", true, addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                addr     = emplacement du point mémoire à traiter.           *
*                                                                             *
*  Description : Retire un point d'arrêt basique en mémoire.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_delete_memory_breakpoint(GBinaryDebugger *debugger, virt_t addr)
{
    bool result;                            /* Bilan à retourner           */
    size_t index;                           /* Indice de ce point d'arrêt  */
    raw_breakpoint *bp;                     /* Confort de l'accès rapide   */
    dbg_thread_id_t tid;                    /* Identifiant de thread       */

    g_rw_lock_writer_lock(&debugger->bp_lock);

    result = bsearch_index(&addr, debugger->bpoints, debugger->bp_count, sizeof(raw_breakpoint *),
                           (__compar_fn_t)compare_raw_breakpoint_with_addr, &index);

    if (result)
    {
        bp = debugger->bpoints[index];

        tid = 1;/// FIXME

        result = has_raw_breakpoint_origin(bp, RBO_USER, tid);

        if (result)
        {
            unset_raw_breakpoint_origin(bp, RBO_USER, tid);

            if (is_breakpoint_useless(bp))
                result = g_binary_debugger_remove_memory_breakpoint(debugger, index);

        }

    }

    g_rw_lock_writer_unlock(&debugger->bp_lock);

    if (result)
        g_signal_emit_by_name(debugger, "mem-bp-handled", false, addr);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                            CONTROLE DU FLOT D'EXECUTION                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à redémarrer.                           *
*                                                                             *
*  Description : Redémarre le processus de débogage.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_restart(GBinaryDebugger *debugger)
{
    return G_BINARY_DEBUGGER_GET_CLASS(debugger)->restart(debugger);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                                                                             *
*  Description : Remet en marche le débogueur courant.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_resume(GBinaryDebugger *debugger)
{
    bool result;                            /* Bilan à retourner           */

    result = G_BINARY_DEBUGGER_GET_CLASS(debugger)->resume(debugger);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à relancer.                             *
*                over     = indique si les appels doivent être sautés ou non. *
*                                                                             *
*  Description : Relance l'exécution pour une seule instruction.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_debugger_stepi(GBinaryDebugger *debugger, bool over)
{
    bool result;                            /* Bilan à retourner           */
    virt_t pc;                              /* Position courante           */
    dbg_thread_id_t tid;                    /* Identifiant de thread       */

    result = g_binary_debugger_get_current_pc(debugger, &pc);

    if (result)
    {
        tid = 1;/// FIXME

        g_rw_lock_writer_lock(&debugger->bp_lock);

        result = g_binary_debugger_spread_breakpoints(debugger, tid, pc, RBO_STEP, over);

        g_rw_lock_writer_unlock(&debugger->bp_lock);

    }

    if (result)
        result = G_BINARY_DEBUGGER_GET_CLASS(debugger)->resume(debugger);

    return result;

}
