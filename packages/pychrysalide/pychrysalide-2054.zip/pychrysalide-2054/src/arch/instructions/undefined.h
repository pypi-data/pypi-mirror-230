
/* Chrysalide - Outil d'analyse de fichiers binaires
 * undefined.h - prototypes pour les instructions au comportement non défini
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#ifndef _ARCH_INSTRUCTIONS_UNDEFINED_H
#define _ARCH_INSTRUCTIONS_UNDEFINED_H


#include <glib-object.h>


#include "../instruction.h"
#include "../vmpa.h"



#define G_TYPE_UNDEF_INSTRUCTION            g_undef_instruction_get_type()
#define G_UNDEF_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_UNDEF_INSTRUCTION, GUndefInstruction))
#define G_IS_UNDEF_INSTRUCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_UNDEF_INSTRUCTION))
#define G_UNDEF_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_UNDEF_INSTRUCTION, GUndefInstructionClass))
#define G_IS_UNDEF_INSTRUCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_UNDEF_INSTRUCTION))
#define G_UNDEF_INSTRUCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_UNDEF_INSTRUCTION, GUndefInstructionClass))


/* Définition générique d'une instruction au comportement non défini (instance) */
typedef struct _GUndefInstruction GUndefInstruction;

/* Définition générique d'une instruction au comportement non défini (classe) */
typedef struct _GUndefInstructionClass GUndefInstructionClass;


/* Etat précis de l'instruction */
typedef enum _InstrExpectedBehavior
{
    IEB_NOP,
    IEB_UNDEFINED,
    IEB_UNPREDICTABLE,
    IEB_RESERVED,

} InstrExpectedBehavior;


/* Indique le type défini pour une instruction au comportement non défini. */
GType g_undef_instruction_get_type(void);

/* Crée une instruction au comportement nominalement indéfini. */
GArchInstruction *g_undef_instruction_new(InstrExpectedBehavior);

/* Indique le type de conséquences réél de l'instruction. */
InstrExpectedBehavior g_undef_instruction_get_behavior(const GUndefInstruction *);



#endif  /* _ARCH_INSTRUCTIONS_UNDEFINED_H */
