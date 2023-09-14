
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - gestion des instructions JVM
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


#include "instruction.h"


#include "../instruction-int.h" 



/* Définition générique d'une instruction d'architecture JVM (instance) */
struct _GJvmInstruction
{
    GArchInstruction parent;                /* A laisser en premier        */

    JvmOpcodes type;                        /* Position dans la liste      */

};

/* Définition générique d'une instruction d'architecture JVM (classe) */
struct _GJvmInstructionClass
{
    GArchInstructionClass parent;           /* A laisser en premier        */

};


/* Initialise la classe des instructions pour JVM. */
static void g_jvm_instruction_class_init(GJvmInstructionClass *);

/* Initialise une instance d'opérande d'architecture JVM. */
static void g_jvm_instruction_init(GJvmInstruction *);



/* --------------------- AIDE A LA MISE EN PLACE D'INSTRUCTIONS --------------------- */


/* Répertoire de toutes les instructions JVM */
typedef struct _jvm_instruction
{
    bool care_of_data;                      /* Devinette = repas ?         */
    bool can_wide;                          /* Instruction étendue ?       */
    bin_t opcode;                           /* Opcode de l'instruction     */

    const char *keyword;                    /* Mot clef de la commande     */

} jvm_instruction;


static jvm_instruction _instructions[JOP_COUNT] = {

    [JOP_NOP] =             { false, false, 0x00, "nop" },
    [JOP_ACONST_NULL] =     { false, false, 0x01, "aconst_null" },
    [JOP_ICONST_M1] =       { true, false, 0x02, "iconst_m1" },
    [JOP_ICONST_0] =        { true, false, 0x03, "iconst_0" },
    [JOP_ICONST_1] =        { true, false, 0x04, "iconst_1" },
    [JOP_ICONST_2] =        { true, false, 0x05, "iconst_2" },
    [JOP_ICONST_3] =        { true, false, 0x06, "iconst_3" },
    [JOP_ICONST_4] =        { true, false, 0x07, "iconst_4" },
    [JOP_ICONST_5] =        { true, false, 0x08, "iconst_5" },



    [JOP_POP] =             { false, false, 0x57, "pop" },
    [JOP_POP2] =            { false, false, 0x58, "pop2" },
    [JOP_DUP] =             { false, false, 0x59, "dup" },
    [JOP_DUP_X1] =          { false, false, 0x5a, "dup_x1" },
    [JOP_DUP_X2] =          { false, false, 0x5b, "dup_x2" },
    [JOP_DUP2] =            { false, false, 0x5c, "dup2" },
    [JOP_DUP2_X1] =         { false, false, 0x5d, "dup2_x1" },
    [JOP_DUP2_X2] =         { false, false, 0x5e, "dup2_x2" },


    [JOP_IADD] =            { false, false, 0x60, "iadd" },


    [JOP_I2L] =             { false, false, 0x85, "i2l" },
    [JOP_I2F] =             { false, false, 0x86, "i2f" },
    [JOP_I2D] =             { false, false, 0x87, "i2d" },
    [JOP_L2I] =             { false, false, 0x88, "l2i" },
    [JOP_L2F] =             { false, false, 0x89, "l2f" },
    [JOP_L2D] =             { false, false, 0x8a, "l2d" },
    [JOP_F2I] =             { false, false, 0x8b, "f2i" },
    [JOP_F2L] =             { false, false, 0x8c, "f2l" },
    [JOP_F2D] =             { false, false, 0x8d, "f2d" },
    [JOP_D2I] =             { false, false, 0x8e, "d2i" },
    [JOP_D2L] =             { false, false, 0x8f, "d2l" },
    [JOP_D2F] =             { false, false, 0x90, "d2f" },
    [JOP_I2B] =             { false, false, 0x91, "i2b" },
    [JOP_I2C] =             { false, false, 0x92, "i2c" },
    [JOP_I2S] =             { false, false, 0x93, "i2s" },


    [JOP_ILOAD_0] =         { true, false, 0x1a, "iload_0" },
    [JOP_ILOAD_1] =         { true, false, 0x1b, "iload_1" },
    [JOP_ILOAD_2] =         { true, false, 0x1c, "iload_2" },
    [JOP_ILOAD_3] =         { true, false, 0x1d, "iload_3" },



    [JOP_ALOAD_0] =         { true, false, 0x2a, "aload_0" },
    [JOP_ALOAD_1] =         { true, false, 0x2b, "aload_1" },
    [JOP_ALOAD_2] =         { true, false, 0x2c, "aload_2" },
    [JOP_ALOAD_3] =         { true, false, 0x2d, "aload_3" },

    [JOP_ISTORE_0] =        { true, false, 0x3b, "istore_0" },
    [JOP_ISTORE_1] =        { true, false, 0x3c, "istore_1" },
    [JOP_ISTORE_2] =        { true, false, 0x3d, "istore_2" },
    [JOP_ISTORE_3] =        { true, false, 0x3e, "istore_3" },

    [JOP_IRETURN] =         { false, false, 0xac, "ireturn" },
    [JOP_LRETURN] =         { false, false, 0xad, "lreturn" },
    [JOP_FRETURN] =         { false, false, 0xae, "freturn" },
    [JOP_DRETURN] =         { false, false, 0xaf, "dreturn" },
    [JOP_ARETURN] =         { false, false, 0xb0, "areturn" },
    [JOP_RETURN] =          { false, false, 0xb1, "return" },
    [JOP_GETSTATIC] =       { false, false, 0xb2, "getstatic" },

    [JOP_INVOKE_VIRTUAL] =  { false, false, 0xb6, "invokevirtual" },
    [JOP_INVOKE_SPECIAL] =  { false, false, 0xb7, "invokespecial" },
    [JOP_INVOKE_STATIC] =   { false, false, 0xb8, "invokestatic" },


    [JOP_MONITOR_ENTER] =   { false, false, 0xc2, "monitorenter" },
    [JOP_MONITOR_EXIT] =    { false, false, 0xc3, "monitorexit" }



};


/* Traduit une instruction en version humainement lisible. */
static const char *jvm_get_instruction_text(const GJvmInstruction *, const GExeFormat *);






/* Indique le type défini pour une instruction d'architecture JVM. */
G_DEFINE_TYPE(GJvmInstruction, g_jvm_instruction, G_TYPE_ARCH_INSTRUCTION);



/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions pour JVM.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_instruction_class_init(GJvmInstructionClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction d'architecture JVM.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_instruction_init(GJvmInstruction *instr)
{
    GArchInstruction *parent;               /* Instance parente            */

    parent = G_ARCH_INSTRUCTION(instr);

    //parent->get_text = (get_instruction_text_fc)jvm_get_instruction_text;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type d'instruction à représenter.                     *
*                                                                             *
*  Description : Crée une instruction pour l'architecture JVM.                *
*                                                                             *
*  Retour      : Architecture mise en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_jvm_instruction_new(JvmOpcodes type)
{
    GArchInstruction *result;               /* Structure à retourner       */

    result = g_object_new(G_TYPE_JVM_INSTRUCTION, NULL);

    G_JVM_INSTRUCTION(result)->type = type;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       AIDE A LA MISE EN PLACE D'INSTRUCTIONS                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux.                       *
*                len  = taille totale des données à analyser.                 *
*                wide = étendue de la future instruction. [OUT]               *
*                care = la lecture de l'instr. veut-elle les opcodes ? [OUT]  *
*                                                                             *
*  Description : Recherche l'identifiant de la prochaine instruction.         *
*                                                                             *
*  Retour      : Identifiant de la prochaine instruction à tenter de charger. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

JvmOpcodes jvm_guess_next_instruction(const bin_t *data, off_t pos, off_t len, bool *wide, bool *care)
{
    JvmOpcodes result;                      /* Identifiant à retourner     */
    bin_t opcode;                           /* Opcode à trouver            */

    *wide = (data[pos] == 0xc4);

    if (*wide && (pos + 1) == len) return JOP_COUNT;

    opcode = data[pos + (*wide ? 1 : 0)];

    for (result = 0; result < JOP_COUNT; result++)
    {
        if (*wide && !_instructions[result].can_wide) continue;

        if (_instructions[result].opcode == opcode)
        {
            *care = _instructions[result].care_of_data;
            break;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction à traiter.                              *
*                format = format du binaire manipulé.                         *
*                                                                             *
*  Description : Traduit une instruction en version humainement lisible.      *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer de la mémoire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *jvm_get_instruction_text(const GJvmInstruction *instr, const GExeFormat *format)
{
    return _instructions[instr->type].keyword;

}
