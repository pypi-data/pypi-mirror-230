
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.c - édition des liens après la phase de désassemblage ARM v7
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


#include "link.h"


#include <assert.h>
#include <arch/operands/register.h>


#include "operands/reglist.h"
#include "../instruction.h"
#include "../register.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARM à traiter.                         *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Encadre les sauts à partir de registres ARMv7.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_armv7_conditional_branch_from_register(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    ArmCondCode cond;                       /* Condition d'exécution       */
    ArchInstrFlag flag;                     /* Fanion particulier appliqué */
    GArchOperand *op;                       /* Opérande numérique en place */
    GArmRegister *reg;                      /* Registre matériel manipulé  */

    cond = g_arm_instruction_get_cond(G_ARM_INSTRUCTION(instr));

    flag = (cond == ACC_AL ? AIF_RETURN_POINT : AIF_COND_RETURN_POINT);

    op = g_arch_instruction_get_operand(instr, 0);
    assert(G_IS_REGISTER_OPERAND(op));

    reg = G_ARM_REGISTER(g_register_operand_get_register(G_REGISTER_OPERAND(op)));

    if (g_arm_register_get_index(reg) == 14 /* lr */)
        g_arch_instruction_set_flag(instr, flag);

    else
    {
        /**
         * On fait un saut mais on ne sait pas vers où !
         *
         * Dans tous les cas, le flot d'exécution ne continue pas naturellement
         * vers l'instruction suivante, donc on marque le branchement comme
         * étant un point de retour.
         */
        g_arch_instruction_set_flag(instr, flag);

    }

    g_object_unref(G_OBJECT(reg));

    g_object_unref(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARM à traiter.                         *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Détecte les fins de procédures à base d'instructions 'pop'.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_armv7_return_from_pop(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    ArmCondCode cond;                       /* Condition d'exécution       */
    ArchInstrFlag flag;                     /* Fanion particulier appliqué */
    GArchOperand *op;                       /* Opérande numérique en place */
    GArmV7RegListOperand *reglist;          /* Autre version de l'instance */
    size_t count;                           /* Nombre de registres présents*/
    size_t i;                               /* Boucle de parcours          */
    GArmRegister *reg;                      /* Registre matériel manipulé  */

    cond = g_arm_instruction_get_cond(G_ARM_INSTRUCTION(instr));

    flag = (cond == ACC_AL ? AIF_RETURN_POINT : AIF_COND_RETURN_POINT);

    op = g_arch_instruction_get_operand(instr, 0);
    assert(G_IS_ARMV7_REGLIST_OPERAND(op));

    reglist = G_ARMV7_REGLIST_OPERAND(op);

    count = g_armv7_reglist_count_registers(reglist);

    for (i = 0; i < count; i++)
    {
        reg = G_ARM_REGISTER(g_armv7_reglist_operand_get_register(reglist, i));

        if (g_arm_register_get_index(reg) == 15 /* pc */)
            g_arch_instruction_set_flag(instr, flag);

        g_object_unref(G_OBJECT(reg));

    }

    g_object_unref(G_OBJECT(op));

}
