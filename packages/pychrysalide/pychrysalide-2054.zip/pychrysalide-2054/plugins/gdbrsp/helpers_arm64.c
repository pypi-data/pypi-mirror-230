
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers_arm64.c - compléments utiles à GDB pour l'architecture AArch64
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


#include "helpers_arm64.h"


#include <malloc.h>


#include "gdb-int.h"



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

bool compute_call_stack_for_arm64(GGdbDebugger *debugger, virt_t **callstack, size_t *size)
{
    bool result;                            /* Bilan global à retourner    */
    GBinaryDebugger *base;                  /* Version basique d'instance  */
    uint64_t fp;                            /* Pointeur de cadre à suivre  */
    uint64_t previous;                      /* Appel de fonction précédent */

    base = G_BINARY_DEBUGGER(debugger);

    result = g_binary_debugger_read_register_u64(base, "x29", &fp);

    while (result && fp != 0)
    {
        result = g_binary_debugger_read_memory_u64(base, fp + sizeof(uint64_t), &previous);
        if (!result) break;

        *callstack = (virt_t *)realloc(*callstack, ++(*size) * sizeof(virt_t));

        (*callstack)[*size - 1] = previous;

        result = g_binary_debugger_read_memory_u64(base, fp, &fp);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                addr     = emplacement du point mémoire à traiter.           *
*                cmd      = commande en cours de constitution. [OUT]          *
*                                                                             *
*  Description : Complète la commande manipulant des points d'arrêt.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool fill_memory_breakpoint_cmd_for_arm64(GGdbDebugger *debugger, virt_t addr, char *cmd)
{
    strcat(cmd, ",4");

    return true;

}
