
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hops_armv7.c - recherche d'appels système spécifiques à ARMv7
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "hops_armv7.h"


#include <assert.h>
#include <string.h>


#include <arch/operands/immediate.h>
#include <plugins/arm/v7/registers/basic.h>



/* Détermine si l'instruction lance un appel syystème. */
static bool is_armv7_linux_syscall(GArchInstruction *);

/* Identifie le numéro d'appel système en cours de manipulation. */
static bool resolve_armv7_linux_syscall_number(tracked_path *, GArchProcessor *, const hunting_ops *, unsigned int *);

/* Marque les registres associés aux n premiers arguments. */
static bool look_for_armv7_linux_syscall_args(tracked_path *, size_t, size_t);

/* Commente autant que possible un appel système brut. */
static void comment_armv7_linux_syscall(tracked_path *, size_t, syscall_info_t *, comment_writer *);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit les opérations spécifiques à ARMv7 pour une chasse.  *
*                                                                             *
*  Retour      : Ensemble d'opérations pour une chasse aux appels système.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const hunting_ops *get_armv7_hunting_ops(void)
{
    static const hunting_ops armv7_hops = {

        .arch = "arm",

        .is_syscall = is_armv7_linux_syscall,
        .resolve_nr = resolve_armv7_linux_syscall_number,
        .look_for_args = look_for_armv7_linux_syscall_args,
        .comment = comment_armv7_linux_syscall

    };

    return &armv7_hops;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction à analyser.                              *
*                                                                             *
*  Description : Détermine si l'instruction lance un appel syystème.          *
*                                                                             *
*  Retour      : Bilan de l'analyse : true s'il s'agit bien d'un appel.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_armv7_linux_syscall(GArchInstruction *instr)
{
    bool result;                            /* Conclusion à diffuser       */
    const char *kwd;                        /* Désignation d'instruction   */

    kwd = g_arch_instruction_get_keyword(instr);

    result = (strcmp(kwd, "svc") == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : exec = suivi de l'utilisation des registres.                 *
*                proc = processeur de l'architecture pour les instructions.   *
*                hops = opérations spécialement adaptées à une architecture.  *
*                nr   = numéro de l'appel système identifié. [OUT]            *
*                                                                             *
*  Description : Identifie le numéro d'appel système en cours de manipulation.*
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool resolve_armv7_linux_syscall_number(tracked_path *exec, GArchProcessor *proc, const hunting_ops *hops, unsigned int *nr)
{
    bool result;                            /* Bilan à faire remonter      */
    GArchRegister *reg;                     /* Registre portant le numéro  */
    bool got_nr;                            /* Bilan d'une recherche       */
    GArchInstruction *instr;                /* Instruction d'importance    */
    const char *kwd;                        /* Désignation d'instruction   */
    GArchOperand *op;                       /* Opérande avec une constante */

    result = false;

    /* On vise r7... */
    reg = g_armv7_basic_register_new(7);
    mark_register_in_tracker(exec, 0, reg, NULL);

    assert(count_register_tracker_stacks(exec) == 1);

    got_nr = look_for_registers(exec, 0, proc, hops);

    if (got_nr)
    {
        instr = get_register_write_location(exec, 0, reg);
        kwd = g_arch_instruction_get_keyword(instr);

        /* ... et uniquement les instructions 'mov r7, <imm>' */
        if (strncmp(kwd, "mov", 3) != 0)
            goto ralsn_exit;

        op = g_arch_instruction_get_operand(instr, 1);

        if (!G_IS_IMM_OPERAND(op))
        {
            g_object_unref(G_OBJECT(op));
            goto ralsn_exit;
        }

        *nr = g_imm_operand_get_raw_value(G_IMM_OPERAND(op));
        result = true;

        g_object_unref(G_OBJECT(op));

    }

 ralsn_exit:

    g_object_unref(G_OBJECT(reg));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : exec = chemin d'exécution à préparer.                        *
*                sid  = identifiant de la pile d'exécution à traiter.         *
*                argc = nombre d'arguments à repérer.                         *
*                                                                             *
*  Description : Marque les registres associés aux n premiers arguments.      *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool look_for_armv7_linux_syscall_args(tracked_path *exec, size_t sid, size_t argc)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t i;                               /* Boucle de parcours          */
    GArchRegister *reg;                     /* Registre portant le numéro  */

    /**
     * man 2 syscall :
     *
     *    arch/ABI   arg1   arg2   arg3   arg4   arg5   arg6   arg7
     *    ──────────────────────────────────────────────────────────
     *    arm/OABI   a1     a2     a3     a4     v1     v2     v3
     *    arm/EABI   r0     r1     r2     r3     r4     r5     r6
     */

    result = (argc <= 7);

    if (result)
        for (i = 0; i < argc; i++)
        {
            reg = g_armv7_basic_register_new(i);
            mark_register_in_tracker(exec, sid, reg, NULL);
            g_object_ref(G_OBJECT(reg));
        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : exec   = chemin d'exécution identifié.                       *
*                sid    = identifiant de la pile d'exécution à traiter.       *
*                info   = fiche d'identité d'un appel système.                *
*                writer = conservateur des commentaires à écrire au final.    *
*                                                                             *
*  Description : Commente autant que possible un appel système brut.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void comment_armv7_linux_syscall(tracked_path *exec, size_t sid, syscall_info_t *info, comment_writer *writer)
{
    GArchRegister *reg;                     /* Registre intervenant        */
    GArchInstruction *instr;                /* Instruction impliquée       */
    size_t i;                               /* Boucle de parcours          */

    /* Type d'appel système */

    reg = g_armv7_basic_register_new(7);

    instr = get_register_write_location(exec, sid, reg);

    if (instr != NULL)
    {
        add_comment_at(writer, info->name, instr);
        g_object_unref(G_OBJECT(instr));
    }

    g_object_unref(G_OBJECT(reg));

    /* Eventuels arguments */

    for (i = 0; i < info->argc; i++)
    {
        reg = g_armv7_basic_register_new(i);

        instr = get_register_write_location(exec, sid, reg);

        if (instr != NULL)
        {
            add_comment_at(writer, info->argv[i], instr);
            g_object_unref(G_OBJECT(instr));
        }

        g_object_unref(G_OBJECT(reg));

    }

}
