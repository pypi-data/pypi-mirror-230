
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - prototypes pour la gestion des instructions de la VM Dalvik
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


#ifndef _PLUGINS_DALVIK_INSTRUCTION_H
#define _PLUGINS_DALVIK_INSTRUCTION_H


#include <arch/instruction.h>



#define G_TYPE_DALVIK_INSTRUCTION            g_dalvik_instruction_get_type()
#define G_DALVIK_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_INSTRUCTION, GDalvikInstruction))
#define G_IS_DALVIK_INSTRUCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_INSTRUCTION))
#define G_DALVIK_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_INSTRUCTION, GDalvikInstructionClass))
#define G_IS_DALVIK_INSTRUCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_INSTRUCTION))
#define G_DALVIK_INSTRUCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_INSTRUCTION, GDalvikInstructionClass))


/* Définition générique d'une instruction d'architecture Dalvik (instance) */
typedef struct _GDalvikInstruction GDalvikInstruction;

/* Définition générique d'une instruction d'architecture Dalvik (classe) */
typedef struct _GDalvikInstructionClass GDalvikInstructionClass;


/* Indique le type défini pour une instruction d'architecture Dalvik. */
GType g_dalvik_instruction_get_type(void);



#endif  /* _PLUGINS_DALVIK_INSTRUCTION_H */
