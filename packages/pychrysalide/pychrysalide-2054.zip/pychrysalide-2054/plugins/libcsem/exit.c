
/* Chrysalide - Outil d'analyse de fichiers binaires
 * exit.c - définition des sorties comme points de non retour
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "exit.h"


#include <format/format.h>



/* Modifie toutes les instructions appelant exit(). */
static void mark_one_kind_of_exit_as_return(const GLoadedBinary *, const char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire dont le contenu est en cours de traitement. *
*                                                                             *
*  Description : Modifie toutes les instructions appelant exit().             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mark_one_kind_of_exit_as_return(const GLoadedBinary *binary, const char *fname)
{
    GBinFormat *format;                     /* Format du fichier binaire   */
    GBinSymbol *symbol;                     /* Symbole de fonction trouvé  */
    const mrange_t *range;                  /* Emplacement du symbole      */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    GArchInstruction *instr;                /* Instruction de sortie       */
    size_t count;                           /* Nbre de sources affichées   */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *source;             /* Instruction diverse liée    */

    format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    if (!g_binary_format_find_symbol_by_label(format, fname, &symbol))
        goto mokoear_exit;

    if (g_binary_symbol_get_stype(symbol) != STP_ROUTINE)
        goto mokoear_done_with_sym;

    range = g_binary_symbol_get_range(symbol);

    proc = g_loaded_binary_get_processor(binary);

    instr = g_arch_processor_find_instr_by_address(proc,  get_mrange_addr(range));

    if (instr == NULL)
        goto mokoear_not_found;

    g_arch_instruction_lock_src(instr);

    count = g_arch_instruction_count_sources(instr);

    for (i = 0; i < count; i++)
    {
        source = g_arch_instruction_get_source(instr, i);

        if (source->type == ILT_CALL)
            g_arch_instruction_set_flag(source->linked, AIF_RETURN_POINT);

        unref_instr_link(source);

    }

    g_arch_instruction_unlock_src(instr);

    g_object_unref(G_OBJECT(instr));

 mokoear_not_found:

    g_object_unref(G_OBJECT(proc));

 mokoear_done_with_sym:

    g_object_unref(G_OBJECT(symbol));

 mokoear_exit:

    g_object_unref(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire dont le contenu est en cours de traitement. *
*                                                                             *
*  Description : Modifie toutes les instructions appelant exit().             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void mark_exit_calls_as_return_instructions(const GLoadedBinary *binary)
{
    const char **iter;                      /* Boucle de parcours          */

    static const char *exit_functions[] = {
        "exit",
        "_exit",
        "_Exit",
        NULL
    };

    for (iter = exit_functions; *iter != NULL; iter++)
        mark_one_kind_of_exit_as_return(binary, *iter);

}
