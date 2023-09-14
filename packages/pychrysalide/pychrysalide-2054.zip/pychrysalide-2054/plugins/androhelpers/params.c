
/* Chrysalide - Outil d'analyse de fichiers binaires
 * params.c - affichage plus adapté des registres liés à des paramètres
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#include "params.h"


#include <stdio.h>


#include <arch/dalvik/operands/args.h>
#include <arch/dalvik/operands/register.h>
#include <format/dex/dex-int.h>
#include <format/dex/method.h>



/* Procède si nécessaire au remplacement du texte de l'opérande. */
static void process_register_operand(const GDexMethod *, GArchOperand *);

/* Parcours en profondeur un ensemble d'arguments. */
static void process_args_operand(const GDexMethod *, const GDalvikArgsOperand *);

/* Visite chaque opérande des instructions d'une méthode. */
static void visit_all_method_operands(const GDexMethod *, GArchInstruction *);



/******************************************************************************
*                                                                             *
*  Paramètres  : method  = routine en cours de parcours.                      *
*                operand = morceau d'instruction en cours de traitement.      *
*                                                                             *
*  Description : Procède si nécessaire au remplacement du texte de l'opérande.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void process_register_operand(const GDexMethod *method, GArchOperand *operand)
{
    GDalvikRegister *reg;                   /* Registre représenté         */
    uint16_t index;                         /* Indice de ce registre       */
    DexVariableIndex info;                  /* Nature réelle du registre   */
    char tmp[12 /* 4294967295U */];         /* Construction du texte       */

    reg = g_dalvik_register_operand_get(G_DALVIK_REGISTER_OPERAND(operand));
    index = g_dalvik_register_get_index(reg);

    info = g_dex_method_get_variable(method, index);

    if (info & DVI_THIS)
        g_arch_operand_set_alt_text(operand, "this", RTT_REGISTER);

    else if (info & DVI_ARGUMENT)
    {
        snprintf(tmp, 12, "p%u", (unsigned int)DVI_INDEX(info));
        g_arch_operand_set_alt_text(operand, tmp, RTT_REGISTER);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = routine en cours de parcours.                       *
*                args   = liste d'opérandes à analyser.                       *
*                                                                             *
*  Description : Parcours en profondeur un ensemble d'arguments.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void process_args_operand(const GDexMethod *method, const GDalvikArgsOperand *args)
{
    size_t count;                           /* Nombre d'opérandes          */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *operand;                  /* Operande à manipuler        */

    count = g_dalvik_args_count(args);

    for (i = 0; i < count; i++)
    {
        operand = g_dalvik_args_operand_get(args, i);

        if (G_IS_DALVIK_REGISTER_OPERAND(operand))
            process_register_operand(method, operand);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = routine à venir parcourir.                          *
*                instrs = liste des instructions pour tout le binaire.        *
*                                                                             *
*  Description : Visite chaque opérande des instructions d'une méthode.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void visit_all_method_operands(const GDexMethod *method, GArchInstruction *instrs)
{
    GBinRoutine *routine;                   /* Abstraction de la méthode   */
    const mrange_t *range;                  /* Emplacement du symbole      */
    vmpa_t start;                           /* Début de la zone couverte   */
    vmpa_t end;                             /* Fin de la zone couverte     */
    GArchInstruction *iter;                 /* Boucle de parcours #1       */
    size_t count;                           /* Nombre d'opérandes          */
    size_t i;                               /* Boucle de parcours #2       */
    GArchOperand *operand;                  /* Operande à manipuler        */

    routine = g_dex_method_get_routine(method);
    range = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

    start = get_mrange_addr(range)->virtual;
    end = start + get_mrange_length(range);

    g_object_unref(G_OBJECT(routine));

    for (iter = g_arch_instruction_find_by_address(instrs, start, true);
         iter != NULL;
         iter = g_arch_instruction_get_next_iter(instrs, iter, end))
    {
        g_arch_instruction_lock_operands(iter);

        count = _g_arch_instruction_count_operands(iter);

        for (i = 0; i < count; i++)
        {
            operand = _g_arch_instruction_get_operand(iter, i);

            if (G_IS_DALVIK_REGISTER_OPERAND(operand))
                process_register_operand(method, operand);

            else if (G_IS_DALVIK_ARGS_OPERAND(operand))
                process_args_operand(method, G_DALVIK_ARGS_OPERAND(operand));

            g_object_unref(G_OBJECT(operand));

        }

        g_arch_instruction_unlock_operands(iter);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = représentation binaire à traiter.                   *
*                                                                             *
*  Description : Effectue le remplacement de tous les paramètres.             *
*                                                                             *
*  Retour      : true si une action a été menée, false sinon.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool replace_parameters(GLoadedBinary *binary)
{
    GDexFormat *format;                     /* Format du binaire chargé    */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GArchInstruction *instrs;               /* Instructions Dalvik         */
    size_t cls_count;                       /* Nombre de classes trouvées  */
    size_t i;                               /* Boucle de parcours #1       */
    GDexClass *class;                       /* Classe à analyser           */
    size_t meth_count;                      /* Nombre de méthodes trouvées */
    size_t j;                               /* Boucle de parcours #2       */
    GDexMethod *method;                     /* Méthode à parcourir         */

    format = G_DEX_FORMAT(g_loaded_binary_get_format(binary));
    proc = g_loaded_binary_get_processor(binary);
    instrs = NULL;//g_arch_processor_get_disassembled_instructions(proc);

    cls_count = g_dex_format_count_classes(format);
    for (i = 0; i < cls_count; i++)
    {
        class = g_dex_format_get_class(format, i);

        meth_count = g_dex_class_count_methods(class, false);
        for (j = 0; j < meth_count; j++)
        {
            method = g_dex_class_get_method(class, false, j);
            visit_all_method_operands(method, instrs);
            g_object_unref(G_OBJECT(method));
        }

        meth_count = g_dex_class_count_methods(class, true);
        for (j = 0; j < meth_count; j++)
        {
            method = g_dex_class_get_method(class, true, j);
            visit_all_method_operands(method, instrs);
            g_object_unref(G_OBJECT(method));
        }

        g_object_unref(G_OBJECT(class));

    }

    g_object_unref(G_OBJECT(proc));
    g_object_unref(G_OBJECT(format));

    return true;

}
