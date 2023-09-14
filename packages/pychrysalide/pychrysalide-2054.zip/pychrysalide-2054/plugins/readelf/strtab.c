
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strtab.h - présentation des chaînes liées au format des binaires ELF
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "strtab.h"


#include <assert.h>
#include <ctype.h>


#include <arch/instructions/raw.h>
#include <format/strsym.h>
#include <plugins/elf/section.h>



/* Affiche les chaînes présentes dans une zone de données. */
static void parse_elf_string_table(GElfFormat *, GPreloadInfo *, const GBinContent *, const mrange_t *, GtkStatusStack *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à compléter.           *
*                info    = informations à constituer en avance de phase.      *
*                content = contenu binaire à analyser.                        *
*                range   = espace à couvrir pendant l'analyse.                *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Affiche les chaînes présentes dans une zone de données.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void parse_elf_string_table(GElfFormat *format, GPreloadInfo *info, const GBinContent *content, const mrange_t *range, GtkStatusStack *status)
{
    phys_t length;                          /* Taille de la couverture     */
    vmpa2t pos;                             /* Tête de lecture             */
    const bin_t *data;                      /* Donnés à parcourir          */
    bool cut;                               /* Séparation nette ?          */
    GBinFormat *base;                       /* Autre version du format     */
    phys_t i;                               /* Boucle de parcours          */
    phys_t end;                             /* Position de fin de chaîne   */
    GArchInstruction *instr;                /* Instruction décodée         */
    bool inserted;                          /* Bilan d'une insertion       */
    const mrange_t *irange;                 /* Espace occupé par une chaîne*/
    GBinSymbol *symbol;                     /* Symbole à intégrer          */

    length = get_mrange_length(range);

    copy_vmpa(&pos, get_mrange_addr(range));
    data = g_binary_content_get_raw_access(content, &pos, length);

    /**
     * Si la section demandée est anormalement grande (cf. exemple de la suite de
     * tests "tests/format/elf/oob_section_name.asm")...
     */
    if (data == NULL) return;

    /* Boucle de parcours */

    cut = true;

    base = G_BIN_FORMAT(format);

    for (i = 0; i < length; i++)
        if (isprint(data[i]))
        {
            for (end = i + 1; end < length; end++)
                if (!isprint(data[end])) break;

            if (end < length && isspace(data[end]))
                end++;

            if (end < length && data[end] == '\0')
                end++;

            copy_vmpa(&pos, get_mrange_addr(range));
            advance_vmpa(&pos, i);

            instr = g_raw_instruction_new_array(content, MDS_8_BITS, end - i, &pos, MDS_UNDEFINED);
            assert(instr != NULL);

            g_raw_instruction_mark_as_string(G_RAW_INSTRUCTION(instr), true);

            /**
             * Comme g_preload_info_add_instruction() peut consommer l'instruction
             * et qu'on réutilise cette dernière ensuite avec g_arch_instruction_get_range()...
             */
            g_object_ref(G_OBJECT(instr));

            inserted = g_preload_info_add_instruction(info, instr);

            if (inserted)
            {
                irange = g_arch_instruction_get_range(instr);

                symbol = g_string_symbol_new_read_only(SET_GUESS, G_KNOWN_FORMAT(base), irange);

                g_object_ref(G_OBJECT(symbol));

                g_binary_format_add_symbol(base, symbol);

                /* Jointure avec la chaîne précédente ? */

                if (cut)
                    g_string_symbol_build_label(G_STR_SYMBOL(symbol), base);

                g_object_unref(G_OBJECT(symbol));

            }

            g_object_unref(G_OBJECT(instr));

            /* Conclusion */

            cut = (data[end - 1] == '\0');

            i = end - 1;

        }
        else cut = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Affiche les chaînes liées aux sections ELF.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void show_elf_section_string_table(GElfFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    GBinContent *content;                   /* Contenu binaire à lire      */
    mrange_t range;                         /* Espace à parcourir          */
    bool found;                             /* Détection d'une section     */

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    found = find_elf_section_range_by_name(format, ".interp", &range);

    if (found)
        parse_elf_string_table(format, info, content, &range, status);

    found = find_elf_section_range_by_name(format, ".shstrtab", &range);

    if (found)
        parse_elf_string_table(format, info, content, &range, status);

    found = find_elf_section_range_by_name(format, ".strtab", &range);

    if (found)
        parse_elf_string_table(format, info, content, &range, status);

    g_object_unref(G_OBJECT(content));

}
