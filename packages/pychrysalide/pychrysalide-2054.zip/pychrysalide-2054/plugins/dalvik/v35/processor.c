
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - manipulation du processeur de la VM Dalvik
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include <assert.h>


#include "instruction.h"
#include "opcodes/identifiers.h"
#include "opcodes/opcodes.h"
#include "../processor-int.h"
#include "../pseudo/fill.h"
#include "../pseudo/switch.h"



/* Définition du processeur de la VM Dalvik v35 (instance) */
struct _GDalvik35Processor
{
    GDalvikProcessor parent;                /* Instance parente            */

};


/* Définition du processeur de la VM Dalvik v35 (classe) */
struct _GDalvik35ProcessorClass
{
    GDalvikProcessorClass parent;           /* Classe parente              */

};


/* Initialise la classe des processeurs de VM Dalvik v35. */
static void g_dalvik35_processor_class_init(GDalvik35ProcessorClass *);

/* Initialise une instance de processeur de VM Dalvik v35. */
static void g_dalvik35_processor_init(GDalvik35Processor *);

/* Supprime toutes les références externes. */
static void g_dalvik35_processor_dispose(GDalvik35Processor *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik35_processor_finalize(GDalvik35Processor *);

/* Fournit la désignation interne du processeur d'architecture. */
static char *g_dalvik35_processor_get_key(const GDalvik35Processor *);

/* Fournit le nom humain de l'architecture visée. */
static char *g_dalvik35_processor_get_desc(const GDalvik35Processor *);

/* Décode une instruction dans un flux de données. */
static GArchInstruction *g_dalvik35_processor_disassemble(const GArchProcessor *, GDalvikContext *, const GBinContent *, vmpa2t *, GExeFormat *);



/* Indique le type défini par la GLib pour le processeur Dalvik v35. */
G_DEFINE_TYPE(GDalvik35Processor, g_dalvik35_processor, G_TYPE_DALVIK_PROCESSOR);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des processeurs de VM Dalvik v35.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_processor_class_init(GDalvik35ProcessorClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchProcessorClass *proc;              /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik35_processor_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik35_processor_finalize;

    proc = G_ARCH_PROCESSOR_CLASS(klass);

    proc->get_key = (get_processor_key_fc)g_dalvik35_processor_get_key;
    proc->get_desc = (get_processor_desc_fc)g_dalvik35_processor_get_desc;

    proc->disassemble = (disass_instr_fc)g_dalvik35_processor_disassemble;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de processeur de VM Dalvik v35.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_processor_init(GDalvik35Processor *proc)
{

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

static void g_dalvik35_processor_dispose(GDalvik35Processor *proc)
{
    G_OBJECT_CLASS(g_dalvik35_processor_parent_class)->dispose(G_OBJECT(proc));

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

static void g_dalvik35_processor_finalize(GDalvik35Processor *proc)
{
    G_OBJECT_CLASS(g_dalvik35_processor_parent_class)->finalize(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée le support de l'architecture Dalvik v35.                *
*                                                                             *
*  Retour      : Architecture mise en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchProcessor *g_dalvik35_processor_new(void)
{
    GArchProcessor *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_DALVIK_PROCESSOR, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la désignation interne du processeur d'architecture. *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_dalvik35_processor_get_key(const GDalvik35Processor *proc)
{
    char *result;                           /* Désignation à renvoyer      */

    result = strdup("dalvik35");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'architecture visée.               *
*                                                                             *
*  Retour      : Désignation humaine associée au processeur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_dalvik35_processor_get_desc(const GDalvik35Processor *proc)
{
    char *result;                           /* Désignation à renvoyer      */

    result = strdup("Dalvik Virtual Machine v35");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = architecture visée par la procédure.               *
*                ctx     = contexte lié à l'exécution du processeur.          *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                format  = format du fichier contenant le code.               *
*                                                                             *
*  Description : Désassemble une instruction dans un flux de données.         *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *g_dalvik35_processor_disassemble(const GArchProcessor *proc, GDalvikContext *ctx, const GBinContent *content, vmpa2t *pos, GExeFormat *format)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint8_t raw8;                           /* Donnée de 8 bits à analyser */
    bool pseudo_handled;                    /* Détection de pseudo-instruc.*/
    Dalvik35Opcodes id;                     /* Identifiant d'instruction   */

    static const disass_instr_fc decodings[DOP35_COUNT] = {

        [DOP35_NOP]                    = dalvik35_read_instr_nop,
        [DOP35_MOVE]                   = dalvik35_read_instr_move,
        [DOP35_MOVE_FROM16]            = dalvik35_read_instr_move_from16,
        [DOP35_MOVE_16]                = dalvik35_read_instr_move_16,
        [DOP35_MOVE_WIDE]              = dalvik35_read_instr_move_wide,
        [DOP35_MOVE_WIDE_FROM16]       = dalvik35_read_instr_move_wide_from16,
        [DOP35_MOVE_WIDE_16]           = dalvik35_read_instr_move_wide_16,
        [DOP35_MOVE_OBJECT]            = dalvik35_read_instr_move_object,
        [DOP35_MOVE_OBJECT_FROM16]     = dalvik35_read_instr_move_object_from16,
        [DOP35_MOVE_OBJECT_16]         = dalvik35_read_instr_move_object_16,
        [DOP35_MOVE_RESULT]            = dalvik35_read_instr_move_result,
        [DOP35_MOVE_RESULT_WIDE]       = dalvik35_read_instr_move_result_wide,
        [DOP35_MOVE_RESULT_OBJECT]     = dalvik35_read_instr_move_result_object,
        [DOP35_MOVE_EXCEPTION]         = dalvik35_read_instr_move_exception,
        [DOP35_RETURN_VOID]            = dalvik35_read_instr_return_void,
        [DOP35_RETURN]                 = dalvik35_read_instr_return,
        [DOP35_RETURN_WIDE]            = dalvik35_read_instr_return_wide,
        [DOP35_RETURN_OBJECT]          = dalvik35_read_instr_return_object,
        [DOP35_CONST_4]                = dalvik35_read_instr_const_4,
        [DOP35_CONST_16]               = dalvik35_read_instr_const_16,
        [DOP35_CONST]                  = dalvik35_read_instr_const,
        [DOP35_CONST_HIGH16]           = dalvik35_read_instr_const_high16,
        [DOP35_CONST_WIDE_16]          = dalvik35_read_instr_const_wide_16,
        [DOP35_CONST_WIDE_32]          = dalvik35_read_instr_const_wide_32,
        [DOP35_CONST_WIDE]             = dalvik35_read_instr_const_wide,
        [DOP35_CONST_WIDE_HIGH16]      = dalvik35_read_instr_const_wide_high16,
        [DOP35_CONST_STRING]           = dalvik35_read_instr_const_string,
        [DOP35_CONST_STRING_JUMBO]     = dalvik35_read_instr_const_string_jumbo,
        [DOP35_CONST_CLASS]            = dalvik35_read_instr_const_class,
        [DOP35_MONITOR_ENTER]          = dalvik35_read_instr_monitor_enter,
        [DOP35_MONITOR_EXIT]           = dalvik35_read_instr_monitor_exit,
        [DOP35_CHECK_CAST]             = dalvik35_read_instr_check_cast,
        [DOP35_INSTANCE_OF]            = dalvik35_read_instr_instance_of,
        [DOP35_ARRAY_LENGTH]           = dalvik35_read_instr_array_length,
        [DOP35_NEW_INSTANCE]           = dalvik35_read_instr_new_instance,
        [DOP35_NEW_ARRAY]              = dalvik35_read_instr_new_array,
        [DOP35_FILLED_NEW_ARRAY]       = dalvik35_read_instr_filled_new_array,
        [DOP35_FILLED_NEW_ARRAY_RANGE] = dalvik35_read_instr_filled_new_array_range,
        [DOP35_FILL_ARRAY_DATA]        = dalvik35_read_instr_fill_array_data,
        [DOP35_THROW]                  = dalvik35_read_instr_throw,
        [DOP35_GOTO]                   = dalvik35_read_instr_goto,
        [DOP35_GOTO_16]                = dalvik35_read_instr_goto_16,
        [DOP35_GOTO_32]                = dalvik35_read_instr_goto_32,
        [DOP35_PACKED_SWITCH]          = dalvik35_read_instr_packed_switch,
        [DOP35_SPARSE_SWITCH]          = dalvik35_read_instr_sparse_switch,
        [DOP35_CMPL_FLOAT]             = dalvik35_read_instr_cmpl_float,
        [DOP35_CMPG_FLOAT]             = dalvik35_read_instr_cmpg_float,
        [DOP35_CMPL_DOUBLE]            = dalvik35_read_instr_cmpl_double,
        [DOP35_CMPG_DOUBLE]            = dalvik35_read_instr_cmpg_double,
        [DOP35_CMP_LONG]               = dalvik35_read_instr_cmp_long,
        [DOP35_IF_EQ]                  = dalvik35_read_instr_if_eq,
        [DOP35_IF_NE]                  = dalvik35_read_instr_if_ne,
        [DOP35_IF_LT]                  = dalvik35_read_instr_if_lt,
        [DOP35_IF_GE]                  = dalvik35_read_instr_if_ge,
        [DOP35_IF_GT]                  = dalvik35_read_instr_if_gt,
        [DOP35_IF_LE]                  = dalvik35_read_instr_if_le,
        [DOP35_IF_EQZ]                 = dalvik35_read_instr_if_eqz,
        [DOP35_IF_NEZ]                 = dalvik35_read_instr_if_nez,
        [DOP35_IF_LTZ]                 = dalvik35_read_instr_if_ltz,
        [DOP35_IF_GEZ]                 = dalvik35_read_instr_if_gez,
        [DOP35_IF_GTZ]                 = dalvik35_read_instr_if_gtz,
        [DOP35_IF_LEZ]                 = dalvik35_read_instr_if_lez,
        [DOP35_UNUSED_3E]              = dalvik35_read_instr_unused_3e,
        [DOP35_UNUSED_3F]              = dalvik35_read_instr_unused_3f,
        [DOP35_UNUSED_40]              = dalvik35_read_instr_unused_40,
        [DOP35_UNUSED_41]              = dalvik35_read_instr_unused_41,
        [DOP35_UNUSED_42]              = dalvik35_read_instr_unused_42,
        [DOP35_UNUSED_43]              = dalvik35_read_instr_unused_43,
        [DOP35_AGET]                   = dalvik35_read_instr_aget,
        [DOP35_AGET_WIDE]              = dalvik35_read_instr_aget_wide,
        [DOP35_AGET_OBJECT]            = dalvik35_read_instr_aget_object,
        [DOP35_AGET_BOOLEAN]           = dalvik35_read_instr_aget_boolean,
        [DOP35_AGET_BYTE]              = dalvik35_read_instr_aget_byte,
        [DOP35_AGET_CHAR]              = dalvik35_read_instr_aget_char,
        [DOP35_AGET_SHORT]             = dalvik35_read_instr_aget_short,
        [DOP35_APUT]                   = dalvik35_read_instr_aput,
        [DOP35_APUT_WIDE]              = dalvik35_read_instr_aput_wide,
        [DOP35_APUT_OBJECT]            = dalvik35_read_instr_aput_object,
        [DOP35_APUT_BOOLEAN]           = dalvik35_read_instr_aput_boolean,
        [DOP35_APUT_BYTE]              = dalvik35_read_instr_aput_byte,
        [DOP35_APUT_CHAR]              = dalvik35_read_instr_aput_char,
        [DOP35_APUT_SHORT]             = dalvik35_read_instr_aput_short,
        [DOP35_IGET]                   = dalvik35_read_instr_iget,
        [DOP35_IGET_WIDE]              = dalvik35_read_instr_iget_wide,
        [DOP35_IGET_OBJECT]            = dalvik35_read_instr_iget_object,
        [DOP35_IGET_BOOLEAN]           = dalvik35_read_instr_iget_boolean,
        [DOP35_IGET_BYTE]              = dalvik35_read_instr_iget_byte,
        [DOP35_IGET_CHAR]              = dalvik35_read_instr_iget_char,
        [DOP35_IGET_SHORT]             = dalvik35_read_instr_iget_short,
        [DOP35_IPUT]                   = dalvik35_read_instr_iput,
        [DOP35_IPUT_WIDE]              = dalvik35_read_instr_iput_wide,
        [DOP35_IPUT_OBJECT]            = dalvik35_read_instr_iput_object,
        [DOP35_IPUT_BOOLEAN]           = dalvik35_read_instr_iput_boolean,
        [DOP35_IPUT_BYTE]              = dalvik35_read_instr_iput_byte,
        [DOP35_IPUT_CHAR]              = dalvik35_read_instr_iput_char,
        [DOP35_IPUT_SHORT]             = dalvik35_read_instr_iput_short,
        [DOP35_SGET]                   = dalvik35_read_instr_sget,
        [DOP35_SGET_WIDE]              = dalvik35_read_instr_sget_wide,
        [DOP35_SGET_OBJECT]            = dalvik35_read_instr_sget_object,
        [DOP35_SGET_BOOLEAN]           = dalvik35_read_instr_sget_boolean,
        [DOP35_SGET_BYTE]              = dalvik35_read_instr_sget_byte,
        [DOP35_SGET_CHAR]              = dalvik35_read_instr_sget_char,
        [DOP35_SGET_SHORT]             = dalvik35_read_instr_sget_short,
        [DOP35_SPUT]                   = dalvik35_read_instr_sput,
        [DOP35_SPUT_WIDE]              = dalvik35_read_instr_sput_wide,
        [DOP35_SPUT_OBJECT]            = dalvik35_read_instr_sput_object,
        [DOP35_SPUT_BOOLEAN]           = dalvik35_read_instr_sput_boolean,
        [DOP35_SPUT_BYTE]              = dalvik35_read_instr_sput_byte,
        [DOP35_SPUT_CHAR]              = dalvik35_read_instr_sput_char,
        [DOP35_SPUT_SHORT]             = dalvik35_read_instr_sput_short,
        [DOP35_INVOKE_VIRTUAL]         = dalvik35_read_instr_invoke_virtual,
        [DOP35_INVOKE_SUPER]           = dalvik35_read_instr_invoke_super,
        [DOP35_INVOKE_DIRECT]          = dalvik35_read_instr_invoke_direct,
        [DOP35_INVOKE_STATIC]          = dalvik35_read_instr_invoke_static,
        [DOP35_INVOKE_INTERFACE]       = dalvik35_read_instr_invoke_interface,
        [DOP35_UNUSED_73]              = dalvik35_read_instr_unused_73,
        [DOP35_INVOKE_VIRTUAL_RANGE]   = dalvik35_read_instr_invoke_virtual_range,
        [DOP35_INVOKE_SUPER_RANGE]     = dalvik35_read_instr_invoke_super_range,
        [DOP35_INVOKE_DIRECT_RANGE]    = dalvik35_read_instr_invoke_direct_range,
        [DOP35_INVOKE_STATIC_RANGE]    = dalvik35_read_instr_invoke_static_range,
        [DOP35_INVOKE_INTERFACE_RANGE] = dalvik35_read_instr_invoke_interface_range,
        [DOP35_UNUSED_79]              = dalvik35_read_instr_unused_79,
        [DOP35_UNUSED_7A]              = dalvik35_read_instr_unused_7a,
        [DOP35_NEG_INT]                = dalvik35_read_instr_neg_int,
        [DOP35_NOT_INT]                = dalvik35_read_instr_not_int,
        [DOP35_NEG_LONG]               = dalvik35_read_instr_neg_long,
        [DOP35_NOT_LONG]               = dalvik35_read_instr_not_long,
        [DOP35_NEG_FLOAT]              = dalvik35_read_instr_neg_float,
        [DOP35_NEG_DOUBLE]             = dalvik35_read_instr_neg_double,
        [DOP35_INT_TO_LONG]            = dalvik35_read_instr_int_to_long,
        [DOP35_INT_TO_FLOAT]           = dalvik35_read_instr_int_to_float,
        [DOP35_INT_TO_DOUBLE]          = dalvik35_read_instr_int_to_double,
        [DOP35_LONG_TO_INT]            = dalvik35_read_instr_long_to_int,
        [DOP35_LONG_TO_FLOAT]          = dalvik35_read_instr_long_to_float,
        [DOP35_LONG_TO_DOUBLE]         = dalvik35_read_instr_long_to_double,
        [DOP35_FLOAT_TO_INT]           = dalvik35_read_instr_float_to_int,
        [DOP35_FLOAT_TO_LONG]          = dalvik35_read_instr_float_to_long,
        [DOP35_FLOAT_TO_DOUBLE]        = dalvik35_read_instr_float_to_double,
        [DOP35_DOUBLE_TO_INT]          = dalvik35_read_instr_double_to_int,
        [DOP35_DOUBLE_TO_LONG]         = dalvik35_read_instr_double_to_long,
        [DOP35_DOUBLE_TO_FLOAT]        = dalvik35_read_instr_double_to_float,
        [DOP35_INT_TO_BYTE]            = dalvik35_read_instr_int_to_byte,
        [DOP35_INT_TO_CHAR]            = dalvik35_read_instr_int_to_char,
        [DOP35_INT_TO_SHORT]           = dalvik35_read_instr_int_to_short,
        [DOP35_ADD_INT]                = dalvik35_read_instr_add_int,
        [DOP35_SUB_INT]                = dalvik35_read_instr_sub_int,
        [DOP35_MUL_INT]                = dalvik35_read_instr_mul_int,
        [DOP35_DIV_INT]                = dalvik35_read_instr_div_int,
        [DOP35_REM_INT]                = dalvik35_read_instr_rem_int,
        [DOP35_AND_INT]                = dalvik35_read_instr_and_int,
        [DOP35_OR_INT]                 = dalvik35_read_instr_or_int,
        [DOP35_XOR_INT]                = dalvik35_read_instr_xor_int,
        [DOP35_SHL_INT]                = dalvik35_read_instr_shl_int,
        [DOP35_SHR_INT]                = dalvik35_read_instr_shr_int,
        [DOP35_USHR_INT]               = dalvik35_read_instr_ushr_int,
        [DOP35_ADD_LONG]               = dalvik35_read_instr_add_long,
        [DOP35_SUB_LONG]               = dalvik35_read_instr_sub_long,
        [DOP35_MUL_LONG]               = dalvik35_read_instr_mul_long,
        [DOP35_DIV_LONG]               = dalvik35_read_instr_div_long,
        [DOP35_REM_LONG]               = dalvik35_read_instr_rem_long,
        [DOP35_AND_LONG]               = dalvik35_read_instr_and_long,
        [DOP35_OR_LONG]                = dalvik35_read_instr_or_long,
        [DOP35_XOR_LONG]               = dalvik35_read_instr_xor_long,
        [DOP35_SHL_LONG]               = dalvik35_read_instr_shl_long,
        [DOP35_SHR_LONG]               = dalvik35_read_instr_shr_long,
        [DOP35_USHR_LONG]              = dalvik35_read_instr_ushr_long,
        [DOP35_ADD_FLOAT]              = dalvik35_read_instr_add_float,
        [DOP35_SUB_FLOAT]              = dalvik35_read_instr_sub_float,
        [DOP35_MUL_FLOAT]              = dalvik35_read_instr_mul_float,
        [DOP35_DIV_FLOAT]              = dalvik35_read_instr_div_float,
        [DOP35_REM_FLOAT]              = dalvik35_read_instr_rem_float,
        [DOP35_ADD_DOUBLE]             = dalvik35_read_instr_add_double,
        [DOP35_SUB_DOUBLE]             = dalvik35_read_instr_sub_double,
        [DOP35_MUL_DOUBLE]             = dalvik35_read_instr_mul_double,
        [DOP35_DIV_DOUBLE]             = dalvik35_read_instr_div_double,
        [DOP35_REM_DOUBLE]             = dalvik35_read_instr_rem_double,
        [DOP35_ADD_INT_2ADDR]          = dalvik35_read_instr_add_int_2addr,
        [DOP35_SUB_INT_2ADDR]          = dalvik35_read_instr_sub_int_2addr,
        [DOP35_MUL_INT_2ADDR]          = dalvik35_read_instr_mul_int_2addr,
        [DOP35_DIV_INT_2ADDR]          = dalvik35_read_instr_div_int_2addr,
        [DOP35_REM_INT_2ADDR]          = dalvik35_read_instr_rem_int_2addr,
        [DOP35_AND_INT_2ADDR]          = dalvik35_read_instr_and_int_2addr,
        [DOP35_OR_INT_2ADDR]           = dalvik35_read_instr_or_int_2addr,
        [DOP35_XOR_INT_2ADDR]          = dalvik35_read_instr_xor_int_2addr,
        [DOP35_SHL_INT_2ADDR]          = dalvik35_read_instr_shl_int_2addr,
        [DOP35_SHR_INT_2ADDR]          = dalvik35_read_instr_shr_int_2addr,
        [DOP35_USHR_INT_2ADDR]         = dalvik35_read_instr_ushr_int_2addr,
        [DOP35_ADD_LONG_2ADDR]         = dalvik35_read_instr_add_long_2addr,
        [DOP35_SUB_LONG_2ADDR]         = dalvik35_read_instr_sub_long_2addr,
        [DOP35_MUL_LONG_2ADDR]         = dalvik35_read_instr_mul_long_2addr,
        [DOP35_DIV_LONG_2ADDR]         = dalvik35_read_instr_div_long_2addr,
        [DOP35_REM_LONG_2ADDR]         = dalvik35_read_instr_rem_long_2addr,
        [DOP35_AND_LONG_2ADDR]         = dalvik35_read_instr_and_long_2addr,
        [DOP35_OR_LONG_2ADDR]          = dalvik35_read_instr_or_long_2addr,
        [DOP35_XOR_LONG_2ADDR]         = dalvik35_read_instr_xor_long_2addr,
        [DOP35_SHL_LONG_2ADDR]         = dalvik35_read_instr_shl_long_2addr,
        [DOP35_SHR_LONG_2ADDR]         = dalvik35_read_instr_shr_long_2addr,
        [DOP35_USHR_LONG_2ADDR]        = dalvik35_read_instr_ushr_long_2addr,
        [DOP35_ADD_FLOAT_2ADDR]        = dalvik35_read_instr_add_float_2addr,
        [DOP35_SUB_FLOAT_2ADDR]        = dalvik35_read_instr_sub_float_2addr,
        [DOP35_MUL_FLOAT_2ADDR]        = dalvik35_read_instr_mul_float_2addr,
        [DOP35_DIV_FLOAT_2ADDR]        = dalvik35_read_instr_div_float_2addr,
        [DOP35_REM_FLOAT_2ADDR]        = dalvik35_read_instr_rem_float_2addr,
        [DOP35_ADD_DOUBLE_2ADDR]       = dalvik35_read_instr_add_double_2addr,
        [DOP35_SUB_DOUBLE_2ADDR]       = dalvik35_read_instr_sub_double_2addr,
        [DOP35_MUL_DOUBLE_2ADDR]       = dalvik35_read_instr_mul_double_2addr,
        [DOP35_DIV_DOUBLE_2ADDR]       = dalvik35_read_instr_div_double_2addr,
        [DOP35_REM_DOUBLE_2ADDR]       = dalvik35_read_instr_rem_double_2addr,
        [DOP35_ADD_INT_LIT16]          = dalvik35_read_instr_add_int_lit16,
        [DOP35_RSUB_INT]               = dalvik35_read_instr_rsub_int,
        [DOP35_MUL_INT_LIT16]          = dalvik35_read_instr_mul_int_lit16,
        [DOP35_DIV_INT_LIT16]          = dalvik35_read_instr_div_int_lit16,
        [DOP35_REM_INT_LIT16]          = dalvik35_read_instr_rem_int_lit16,
        [DOP35_AND_INT_LIT16]          = dalvik35_read_instr_and_int_lit16,
        [DOP35_OR_INT_LIT16]           = dalvik35_read_instr_or_int_lit16,
        [DOP35_XOR_INT_LIT16]          = dalvik35_read_instr_xor_int_lit16,
        [DOP35_ADD_INT_LIT8]           = dalvik35_read_instr_add_int_lit8,
        [DOP35_RSUB_INT_LIT8]          = dalvik35_read_instr_rsub_int_lit8,
        [DOP35_MUL_INT_LIT8]           = dalvik35_read_instr_mul_int_lit8,
        [DOP35_DIV_INT_LIT8]           = dalvik35_read_instr_div_int_lit8,
        [DOP35_REM_INT_LIT8]           = dalvik35_read_instr_rem_int_lit8,
        [DOP35_AND_INT_LIT8]           = dalvik35_read_instr_and_int_lit8,
        [DOP35_OR_INT_LIT8]            = dalvik35_read_instr_or_int_lit8,
        [DOP35_XOR_INT_LIT8]           = dalvik35_read_instr_xor_int_lit8,
        [DOP35_SHL_INT_LIT8]           = dalvik35_read_instr_shl_int_lit8,
        [DOP35_SHR_INT_LIT8]           = dalvik35_read_instr_shr_int_lit8,
        [DOP35_USHR_INT_LIT8]          = dalvik35_read_instr_ushr_int_lit8,
        [DOP35_UNUSED_E3]              = dalvik35_read_instr_unused_e3,
        [DOP35_UNUSED_E4]              = dalvik35_read_instr_unused_e4,
        [DOP35_UNUSED_E5]              = dalvik35_read_instr_unused_e5,
        [DOP35_UNUSED_E6]              = dalvik35_read_instr_unused_e6,
        [DOP35_UNUSED_E7]              = dalvik35_read_instr_unused_e7,
        [DOP35_UNUSED_E8]              = dalvik35_read_instr_unused_e8,
        [DOP35_UNUSED_E9]              = dalvik35_read_instr_unused_e9,
        [DOP35_UNUSED_EA]              = dalvik35_read_instr_unused_ea,
        [DOP35_UNUSED_EB]              = dalvik35_read_instr_unused_eb,
        [DOP35_UNUSED_EC]              = dalvik35_read_instr_unused_ec,
        [DOP35_UNUSED_ED]              = dalvik35_read_instr_unused_ed,
        [DOP35_UNUSED_EE]              = dalvik35_read_instr_unused_ee,
        [DOP35_UNUSED_EF]              = dalvik35_read_instr_unused_ef,
        [DOP35_UNUSED_F0]              = dalvik35_read_instr_unused_f0,
        [DOP35_UNUSED_F1]              = dalvik35_read_instr_unused_f1,
        [DOP35_UNUSED_F2]              = dalvik35_read_instr_unused_f2,
        [DOP35_UNUSED_F3]              = dalvik35_read_instr_unused_f3,
        [DOP35_UNUSED_F4]              = dalvik35_read_instr_unused_f4,
        [DOP35_UNUSED_F5]              = dalvik35_read_instr_unused_f5,
        [DOP35_UNUSED_F6]              = dalvik35_read_instr_unused_f6,
        [DOP35_UNUSED_F7]              = dalvik35_read_instr_unused_f7,
        [DOP35_UNUSED_F8]              = dalvik35_read_instr_unused_f8,
        [DOP35_UNUSED_F9]              = dalvik35_read_instr_unused_f9,
        [DOP35_UNUSED_FA]              = dalvik35_read_instr_unused_fa,
        [DOP35_UNUSED_FB]              = dalvik35_read_instr_unused_fb,
        [DOP35_UNUSED_FC]              = dalvik35_read_instr_unused_fc,
        [DOP35_UNUSED_FD]              = dalvik35_read_instr_unused_fd,
        [DOP35_UNUSED_FE]              = dalvik35_read_instr_unused_fe,
        [DOP35_UNUSED_FF]              = dalvik35_read_instr_unused_ff,

    };

    /* Données brutes associées à une instruction ? */

    result = g_dalvik_context_get_raw_data(ctx, content, pos);

    if (result != NULL) goto gdpd_done;

    /* Pseudo-instruction... */

    if (!g_binary_content_read_u8(content, pos, &raw8))
        return NULL;

    result = g_dalvik_processor_disassemble_pseudo(proc, ctx, content, pos, raw8, &pseudo_handled);

    /**
     * Il faut distinguer :
     *
     *    - result == NULL : ce n'était pas une pseudo-instruction.
     *
     *    - result == NULL : c'était une pseudo-instruction, mais un thread
     *      parallèle avait déjà réservé la zone de donnée correspondante.
     *
     * Dans ce dernier cas, on ne chercher pas à désassembler d'avantage,
     * car une pseudo-instruction est déjà en place et on ne veut surtout pas
     * la remplacer par une instruction basique.
     */

    if (result != NULL || pseudo_handled) goto gdpd_done;

    /* ... ou instruction classique */

    assert(raw8 < DOP35_COUNT);

    id = (Dalvik35Opcodes)raw8;

    result = decodings[id](proc, G_PROC_CONTEXT(ctx), content, pos, format);

 gdpd_done:

    return result;

}
