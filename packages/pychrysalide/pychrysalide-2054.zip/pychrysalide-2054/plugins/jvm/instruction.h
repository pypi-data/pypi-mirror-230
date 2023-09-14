
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - prototypes pour la gestion des instructions JVM
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


#ifndef _ARCH_JVM_INSTRUCTION_H
#define _ARCH_JVM_INSTRUCTION_H


#include "../instruction.h"





/* Enumération de tous les opcodes */
typedef enum _JvmOpcodes
{
    JOP_NOP,                                /* nop (0x00)                  */
    JOP_ACONST_NULL,                        /* aconst_null (0x01)          */
    JOP_ICONST_M1,                          /* iconst_m1 (0x02)            */
    JOP_ICONST_0,                           /* iconst_0 (0x03)             */
    JOP_ICONST_1,                           /* iconst_1 (0x04)             */
    JOP_ICONST_2,                           /* iconst_2 (0x05)             */
    JOP_ICONST_3,                           /* iconst_3 (0x06)             */
    JOP_ICONST_4,                           /* iconst_4 (0x07)             */
    JOP_ICONST_5,                           /* iconst_5 (0x08)             */


    JOP_POP,                                /* pop (0x57)                  */
    JOP_POP2,                               /* pop2 (0x58)                 */
    JOP_DUP,                                /* dup (0x59)                  */
    JOP_DUP_X1,                             /* dup_x1 (0x5a)               */
    JOP_DUP_X2,                             /* dup_x2 (0x5b)               */
    JOP_DUP2,                               /* dup2 (0x5c)                 */
    JOP_DUP2_X1,                            /* dup2_x1 (0x5d)              */
    JOP_DUP2_X2,                            /* dup2_x2 (0x5e)              */


    JOP_IADD,                               /* iadd (0x60)                 */


    JOP_I2L,                                /* i2l (0x85)                  */
    JOP_I2F,                                /* i2f (0x86)                  */
    JOP_I2D,                                /* i2d (0x87)                  */
    JOP_L2I,                                /* l2i (0x88)                  */
    JOP_L2F,                                /* l2f (0x89)                  */
    JOP_L2D,                                /* l2d (0x8a)                  */
    JOP_F2I,                                /* f2i (0x8b)                  */
    JOP_F2L,                                /* f2l (0x8c)                  */
    JOP_F2D,                                /* f2d (0x8d)                  */
    JOP_D2I,                                /* d2i (0x8e)                  */
    JOP_D2L,                                /* d2l (0x8f)                  */
    JOP_D2F,                                /* d2f (0x90)                  */
    JOP_I2B,                                /* i2b (0x91)                  */
    JOP_I2C,                                /* i2c (0x92)                  */
    JOP_I2S,                                /* i2s (0x93)                  */




    JOP_ILOAD_0,                            /* iload_0 (0x1a)              */
    JOP_ILOAD_1,                            /* iload_1 (0x1b)              */
    JOP_ILOAD_2,                            /* iload_2 (0x1c)              */
    JOP_ILOAD_3,                            /* iload_3 (0x1d)              */




    JOP_ALOAD_0,                            /* aload_0 (0x2a)              */
    JOP_ALOAD_1,                            /* aload_1 (0x2b)              */
    JOP_ALOAD_2,                            /* aload_2 (0x2c)              */
    JOP_ALOAD_3,                            /* aload_3 (0x2d)              */


    JOP_ISTORE_0,                           /* istore_0 (0x3b)             */
    JOP_ISTORE_1,                           /* istore_1 (0x3c)             */
    JOP_ISTORE_2,                           /* istore_2 (0x3d)             */
    JOP_ISTORE_3,                           /* istore_3 (0x3e)             */


    JOP_IRETURN,                            /* ireturn (0xac)              */
    JOP_LRETURN,                            /* lreturn (0xad)              */
    JOP_FRETURN,                            /* freturn (0xae)              */
    JOP_DRETURN,                            /* dreturn (0xaf)              */
    JOP_ARETURN,                            /* areturn (0xb0)              */
    JOP_RETURN,                             /* return (0xb1)               */
    JOP_GETSTATIC,                          /* getstatic (0xb2)            */

    JOP_INVOKE_VIRTUAL,                     /* invokevirtual (0xb6)        */
    JOP_INVOKE_SPECIAL,                     /* invokespecial (0xb7)        */
    JOP_INVOKE_STATIC,                      /* invokestatic (0xb8)         */

    JOP_MONITOR_ENTER,                      /* monitorenter (0xc2)         */
    JOP_MONITOR_EXIT,                       /* monitorexit (0xc3)          */

    JOP_COUNT

} JvmOpcodes;


#define G_TYPE_JVM_INSTRUCTION            g_jvm_instruction_get_type()
#define G_JVM_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_JVM_INSTRUCTION, GJvmInstruction))
#define G_IS_JVM_INSTRUCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_JVM_INSTRUCTION))
#define G_JVM_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_JVM_INSTRUCTION, GJvmInstructionClass))
#define G_IS_JVM_INSTRUCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_JVM_INSTRUCTION))
#define G_JVM_INSTRUCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_JVM_INSTRUCTION, GJvmInstructionClass))


/* Définition générique d'une instruction d'architecture JVM (instance) */
typedef struct _GJvmInstruction GJvmInstruction;

/* Définition générique d'une instruction d'architecture JVM (classe) */
typedef struct _GJvmInstructionClass GJvmInstructionClass;


/* Indique le type défini pour une instruction d'architecture JVM. */
GType g_jvm_instruction_get_type(void);

/* Crée une instruction pour l'architecture JVM. */
GArchInstruction *g_jvm_instruction_new(JvmOpcodes);



/* --------------------- AIDE A LA MISE EN PLACE D'INSTRUCTIONS --------------------- */


/* Recherche l'identifiant de la prochaine instruction. */
JvmOpcodes jvm_guess_next_instruction(const bin_t *, off_t, off_t, bool *, bool *);



#endif  /* _ARCH_JVM_INSTRUCTION_H */
