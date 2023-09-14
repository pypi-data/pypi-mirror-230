
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.c - édition des liens après la phase de désassemblage ARM
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include <arch/link.h>


#include "cond.h"
#include "instruction.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARM à traiter.                         *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Etablit un lien conditionnel selon une instruction donnée.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_arm_conditional_branch_as_link(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    switch (g_arm_instruction_get_cond(G_ARM_INSTRUCTION(instr)))
    {
        case ACC_AL:
            handle_jump_as_link(instr, proc, context, format);
            break;

        case ACC_NV:
            break;

        default:
            handle_branch_if_true_as_link(instr, proc, context, format);
            break;

    }

}
