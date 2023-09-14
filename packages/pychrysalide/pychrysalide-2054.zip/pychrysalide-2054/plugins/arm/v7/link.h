
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.h - prototypes pour l'édition des liens après la phase de désassemblage ARM v7
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


#ifndef _PLUGINS_ARM_V7_LINK_H
#define _PLUGINS_ARM_V7_LINK_H


#include <arch/instruction.h>


#include "context.h"



/* Encadre les sauts à partir de registres ARMv7. */
void handle_armv7_conditional_branch_from_register(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);

/* Détecte les fins de procédures à base d'instructions 'pop'. */
void handle_armv7_return_from_pop(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);



#endif  /* _PLUGINS_ARM_V7_LINK_H */
