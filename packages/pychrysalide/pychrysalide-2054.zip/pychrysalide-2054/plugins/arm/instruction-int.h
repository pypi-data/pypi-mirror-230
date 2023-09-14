
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction-int.h - prototypes pour la définition générique interne des instructions ARM
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


#ifndef _PLUGINS_ARM_INSTRUCTION_INT_H
#define _PLUGINS_ARM_INSTRUCTION_INT_H


#include <arch/instruction-int.h>


#include "instruction.h"



/* Définition générique d'une instruction d'architecture ARM (instance) */
struct _GArmInstruction
{
    GArchInstruction parent;                /* A laisser en premier        */

    char *suffix;                           /* Complément au nom affiché   */
    char *cached_keyword;                   /* Désignation complète        */

    ArmCondCode cond;                       /* Condition d'exécution       */

};

/* Définition générique d'une instruction d'architecture ARM (classe) */
struct _GArmInstructionClass
{
    GArchInstructionClass parent;           /* A laisser en premier        */

};



#endif  /* _PLUGINS_ARM_INSTRUCTION_INT_H */
