
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers_arm.c - compléments utiles à GDB pour l'architecture ARM
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


#include "helpers_arm.h"


#include <malloc.h>
#include <string.h>


#include "gdb-int.h"



/* Détermine le point d'exécution courant. */
static bool get_arm_pc(GGdbDebugger *, virt_t *);

/* Remonte la pile d'appels jusqu'au point courant. */
static bool compute_call_stack_for_arm(const GGdbDebugger *, virt_t **, size_t *);

/* Complète la commande manipulant des points d'arrêt. */
static const char *get_breakpoint_kind_for_arm(const GGdbDebugger *, virt_t);

/* Construit une instruction provoquant un arrêt d'exécution. */
static const uint8_t *get_arm_breakpoint_data(const GGdbDebugger *, virt_t, size_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit les fonctions adaptées aux opérations pour ARM.      *
*                                                                             *
*  Retour      : Opérations spécifiques adaptées à ARM.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const gdb_arch_ops *get_arm_operations(void)
{
    static const gdb_arch_ops arm_ops = {

        .get_pc = get_arm_pc,
        .compute_cstack = compute_call_stack_for_arm,
        .get_bp_kind = get_breakpoint_kind_for_arm,
        .get_bp_data = get_arm_breakpoint_data

    };

    return &arm_ops;

}


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

static bool get_arm_pc(GGdbDebugger *debugger, virt_t *pc)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t value;

    result = g_binary_debugger_read_register_u32(G_BINARY_DEBUGGER(debugger), "pc", &value);

    if (result)
        *pc = value;

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

static bool compute_call_stack_for_arm(const GGdbDebugger *debugger, virt_t **callstack, size_t *size)
{
    bool result;                            /* Bilan global à retourner    */
    GBinaryDebugger *base;                  /* Version basique d'instance  */
    uint32_t lr;                            /* Retour de fonction          */
    uint32_t fp;                            /* Pointeur de cadre à suivre  */

    base = G_BINARY_DEBUGGER(debugger);

    result = g_binary_debugger_read_register_u32(base, "lr", &lr);

    if (result && lr != 0)
    {
        *callstack = (virt_t *)realloc(*callstack, ++(*size) * sizeof(virt_t));

        (*callstack)[*size - 1] = lr;

    }

    result &= g_binary_debugger_read_register_u32(base, "r11", &fp);

    while (result && fp != 0)
    {
        /**
         * fp[-0] : pc sauvegardé
         * fp[-1] : lr sauvegardé
         * fp[-2] : sp précédent
         * fp[-3] : fp précédent
         */

        result = g_binary_debugger_read_memory_u32(base, fp - 2 * sizeof(uint32_t), &lr);
        if (!result) break;

        if (lr != 0)
        {
            *callstack = (virt_t *)realloc(*callstack, ++(*size) * sizeof(virt_t));

            (*callstack)[*size - 1] = lr;

        }

        result = g_binary_debugger_read_memory_u32(base, fp - 4 * sizeof(uint32_t), &fp);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                virt     = emplacement du point mémoire à traiter.           *
*                                                                             *
*  Description : Complète la commande manipulant des points d'arrêt.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *get_breakpoint_kind_for_arm(const GGdbDebugger *debugger, virt_t virt)
{
    const char *result;                     /* Indication à retourner      */
    GArchProcessor *proc;                   /* Processeur lié au binaire   */
    vmpa2t addr;                            /* Format d'adresse complet    */
    GArchInstruction *instr;                /* Instruction ciblée          */
    const char *encoding;                   /* Encodage de l'instruction   */

    proc = g_loaded_binary_get_processor(G_BINARY_DEBUGGER(debugger)->binary);

    init_vmpa(&addr, VMPA_NO_PHYSICAL, virt);
    instr = g_arch_processor_find_instr_by_address(proc, &addr);

    if (instr == NULL)
        result = NULL;

    else
    {
        encoding = g_arch_instruction_get_encoding(instr);

        if (strcmp(encoding, "Thumb/16") == 0)
            result = ",2";

        if (strcmp(encoding, "Thumb/32") == 0)
            result = ",3";

        if (strcmp(encoding, "ARM") == 0)
            result = ",4";

        else
            result = NULL;

        g_object_unref(G_OBJECT(instr));

    }

    g_object_unref(G_OBJECT(proc));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : debugger = débogueur à manipuler ici.                        *
*                addr     = emplacement du point mémoire à traiter.           *
*                len      = quantité de mémoire à remplacer. [OUT]            *
*                                                                             *
*  Description : Construit une instruction provoquant un arrêt d'exécution.   *
*                                                                             *
*  Retour      : Définition du point d'arrêt à placer à l'adresse donnée.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const uint8_t *get_arm_breakpoint_data(const GGdbDebugger *debugger, virt_t addr, size_t *len)
{
    const uint8_t *result;                  /* Données à placer en mémoire */

    /* Version point d'arrêt */
    static const uint32_t bkpt_code[] = { 0xe1200070 };

    *len = sizeof(bkpt_code);;

    result = (const uint8_t *)bkpt_code;

    return result;

}
