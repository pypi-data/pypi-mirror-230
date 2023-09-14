
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - manipulation du processeur de la JVM
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


#include "processor.h"


#include "instruction.h"
#include "opcodes.h"
#include "../processor-int.h"



/* Définition du processeur de la JVM (instance) */
struct _GJvmProcessor
{
    GArchProcessor parent;                  /* Instance parente            */

};


/* Définition du processeur de la JVM (classe) */
struct _GJvmProcessorClass
{
    GArchProcessorClass parent;             /* Classe parente              */

};


/* Initialise la classe des processeurs de JVM. */
static void g_jvm_processor_class_init(GJvmProcessorClass *);

/* Initialise une instance de processeur de JVM. */
static void g_jvm_processor_init(GJvmProcessor *);

/* Supprime toutes les références externes. */
static void g_jvm_processor_dispose(GJvmProcessor *);

/* Procède à la libération totale de la mémoire. */
static void g_jvm_processor_finalize(GJvmProcessor *);

/* Décode une instruction dans un flux de données. */
static GArchInstruction *g_jvm_processor_decode_instruction(const GJvmProcessor *, const bin_t *, off_t *, off_t, vmpa_t);


/* Indique le type défini par la GLib pour le processeur JVM. */
G_DEFINE_TYPE(GJvmProcessor, g_jvm_processor, G_TYPE_ARCH_PROCESSOR);



/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des processeurs de JVM.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_processor_class_init(GJvmProcessorClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchProcessorClass *proc;              /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_jvm_processor_dispose;
    object->finalize = (GObjectFinalizeFunc)g_jvm_processor_finalize;

    proc = G_ARCH_PROCESSOR_CLASS(klass);

    proc->decode = (decode_instruction_fc)g_jvm_processor_decode_instruction;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de processeur de JVM.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_processor_init(GJvmProcessor *proc)
{
    GArchProcessor *parent;                 /* Instance parente            */

    parent = G_ARCH_PROCESSOR(proc);

    parent->endianness = SRE_BIG;
    parent->memsize = MDS_32_BITS;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_processor_dispose(GJvmProcessor *proc)
{
    G_OBJECT_CLASS(g_jvm_processor_parent_class)->dispose(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_processor_finalize(GJvmProcessor *proc)
{
    G_OBJECT_CLASS(g_jvm_processor_parent_class)->finalize(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée le support de l'architecture JVM.                       *
*                                                                             *
*  Retour      : Architecture mise en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchProcessor *g_jvm_processor_new(void)
{
    GArchProcessor *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_JVM_PROCESSOR, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture visée par la procédure.                  *
*                data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                                                                             *
*  Description : Décode une instruction dans un flux de données.              *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *g_jvm_processor_decode_instruction(const GJvmProcessor *proc, const bin_t *data, off_t *pos, off_t len, vmpa_t addr)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    bool wide;                              /* Utilisation d'étendues      */
    bool care;                              /* Traitement des opcodes      */
    JvmOpcodes id;                          /* Identifiant d'instruction   */

    id = jvm_guess_next_instruction(data, *pos, len, &wide, &care);

    if (id != JOP_COUNT && !care)
    {
        if (wide) (*pos)++;
        (*pos)++;
    }

    switch (id)
    {
        case JOP_NOP:
            result = jvm_read_instr_nop(data, pos, len, addr, proc);
            break;

        case JOP_ACONST_NULL:
            result = jvm_read_instr_aconst_null(data, pos, len, addr, proc);
            break;

        case JOP_ICONST_M1:
        case JOP_ICONST_0:
        case JOP_ICONST_1:
        case JOP_ICONST_2:
        case JOP_ICONST_3:
        case JOP_ICONST_4:
        case JOP_ICONST_5:
            result = jvm_read_instr_iconst_n(data, pos, len, addr, proc);
            break;

        case JOP_POP:
            result = jvm_read_instr_pop(data, pos, len, addr, proc);
            break;

        case JOP_POP2:
            result = jvm_read_instr_pop2(data, pos, len, addr, proc);
            break;

        case JOP_DUP:
            result = jvm_read_instr_dup(data, pos, len, addr, proc);
            break;

        case JOP_DUP_X1:
            result = jvm_read_instr_dup_x1(data, pos, len, addr, proc);
            break;

        case JOP_DUP_X2:
            result = jvm_read_instr_dup_x2(data, pos, len, addr, proc);
            break;

        case JOP_DUP2:
            result = jvm_read_instr_dup2(data, pos, len, addr, proc);
            break;

        case JOP_DUP2_X1:
            result = jvm_read_instr_dup2_x1(data, pos, len, addr, proc);
            break;

        case JOP_DUP2_X2:
            result = jvm_read_instr_dup2_x2(data, pos, len, addr, proc);
            break;

        case JOP_IADD:
            result = jvm_read_instr_iadd(data, pos, len, addr, proc);
            break;

        case JOP_I2L:
            result = jvm_read_instr_i2l(data, pos, len, addr, proc);
            break;

        case JOP_I2F:
            result = jvm_read_instr_i2f(data, pos, len, addr, proc);
            break;

        case JOP_I2D:
            result = jvm_read_instr_i2d(data, pos, len, addr, proc);
            break;

        case JOP_L2I:
            result = jvm_read_instr_l2i(data, pos, len, addr, proc);
            break;

        case JOP_L2F:
            result = jvm_read_instr_l2f(data, pos, len, addr, proc);
            break;

        case JOP_L2D:
            result = jvm_read_instr_l2d(data, pos, len, addr, proc);
            break;

        case JOP_F2I:
            result = jvm_read_instr_f2i(data, pos, len, addr, proc);
            break;

        case JOP_F2L:
            result = jvm_read_instr_f2l(data, pos, len, addr, proc);
            break;

        case JOP_F2D:
            result = jvm_read_instr_f2d(data, pos, len, addr, proc);
            break;

        case JOP_D2I:
            result = jvm_read_instr_d2i(data, pos, len, addr, proc);
            break;

        case JOP_D2L:
            result = jvm_read_instr_d2l(data, pos, len, addr, proc);
            break;

        case JOP_D2F:
            result = jvm_read_instr_d2f(data, pos, len, addr, proc);
            break;

        case JOP_I2B:
            result = jvm_read_instr_i2b(data, pos, len, addr, proc);
            break;

        case JOP_I2C:
            result = jvm_read_instr_i2c(data, pos, len, addr, proc);
            break;

        case JOP_I2S:
            result = jvm_read_instr_i2s(data, pos, len, addr, proc);
            break;

        case JOP_ILOAD_0:
        case JOP_ILOAD_1:
        case JOP_ILOAD_2:
        case JOP_ILOAD_3:
            result = jvm_read_instr_iload_n(data, pos, len, addr, proc);
            break;

        case JOP_ALOAD_0:
        case JOP_ALOAD_1:
        case JOP_ALOAD_2:
        case JOP_ALOAD_3:
            result = jvm_read_instr_aload_n(data, pos, len, addr, proc);
            break;

        case JOP_ISTORE_0:
        case JOP_ISTORE_1:
        case JOP_ISTORE_2:
        case JOP_ISTORE_3:
            result = jvm_read_instr_istore_n(data, pos, len, addr, proc);
            break;

        case JOP_IRETURN:
            result = jvm_read_instr_ireturn(data, pos, len, addr, proc);
            break;

        case JOP_LRETURN:
            result = jvm_read_instr_lreturn(data, pos, len, addr, proc);
            break;

        case JOP_FRETURN:
            result = jvm_read_instr_freturn(data, pos, len, addr, proc);
            break;

        case JOP_DRETURN:
            result = jvm_read_instr_dreturn(data, pos, len, addr, proc);
            break;

        case JOP_ARETURN:
            result = jvm_read_instr_areturn(data, pos, len, addr, proc);
            break;

        case JOP_RETURN:
            result = jvm_read_instr_return(data, pos, len, addr, proc);
            break;

        case JOP_GETSTATIC:
            result = jvm_read_instr_getstatic(data, pos, len, addr, proc);
            break;

        case JOP_INVOKE_VIRTUAL:
            result = jvm_read_instr_invokevirtual(data, pos, len, addr, proc);
            break;

        case JOP_INVOKE_SPECIAL:
            result = jvm_read_instr_invokespecial(data, pos, len, addr, proc);
            break;

        case JOP_INVOKE_STATIC:
            result = jvm_read_instr_invokestatic(data, pos, len, addr, proc);
            break;

        default:
            result = NULL;
            break;

    }

    return result;

}
