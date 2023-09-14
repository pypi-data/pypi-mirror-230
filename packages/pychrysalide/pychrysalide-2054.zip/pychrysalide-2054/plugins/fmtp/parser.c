
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.c - interprétation des champs d'un format binaire
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


#include "parser.h"


#include <assert.h>
#include <string.h>


#include <i18n.h>
#include <arch/instructions/raw.h>
#include <common/extstr.h>
#include <format/known.h>



/* Effectue l'interprétation d'une définition de champ. */
static bool parse_field_definition(const fmt_field_def *, GBinFormat *, GPreloadInfo *, vmpa2t *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : def    = définition de champ à considérer.                   *
*                format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture pour les données.                   *
*                data   = infos complémentaires éventuellement fournies.      *
*                                                                             *
*  Description : Effectue l'interprétation d'une définition de champ.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool parse_field_definition(const fmt_field_def *def, GBinFormat *format, GPreloadInfo *info, vmpa2t *pos, void *data)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    SourceEndian endian;                    /* Boutisme utilisé            */
    vmpa2t mod;                             /* Position  modifiable        */
    GArchInstruction *instr;                /* Instruction décodée         */
    GImmOperand *imm;                       /* Opérande à transformer      */
    size_t i;                               /* Boucle de parcours          */
    char *text;                             /* Texte du commentaire complet*/
    const vmpa2t *addr;                     /* Emplacement d'instruction   */
    GDbComment *comment;                    /* Définition de commentaire   */
    uint64_t raw;                           /* Valeur brute à étudier      */
    const comment_part *part;               /* Accès plus direct           */
    bool inserted;                          /* Bilan d'une insertion       */

    /* Lecture */

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));
    endian = g_binary_format_get_endianness(format);

    if (def->get_value != NULL)
    {
        copy_vmpa(&mod, pos);

        result = def->get_value(def, content, &mod, endian, data);

        if (!result)
            goto pfd_exit;

    }

    if (def->is_uleb128)
        instr = g_raw_instruction_new_uleb128(content, pos);

    else if (def->is_leb128)
        instr = g_raw_instruction_new_sleb128(content, pos);

    else
    {
        assert(def->repeat > 0);
        instr = g_raw_instruction_new_array(content, def->size, def->repeat, pos, endian);
    }

    result = (instr != NULL);

    if (!result)
        goto pfd_exit;

    if (def->is_padding)
        g_raw_instruction_mark_as_padding(G_RAW_INSTRUCTION(instr), true);

    if (def->has_display_rules)
    {
        assert((def->is_uleb128 && def->disp_count == 1)
               || (def->is_leb128 && def->disp_count == 1)
               || (!def->is_uleb128 && !def->is_leb128 && def->disp_count <= def->repeat));

        for (i = 0; i < def->disp_count; i++)
        {
            imm = G_IMM_OPERAND(g_arch_instruction_get_operand(instr, i));

            g_imm_operand_set_default_display(imm, def->disp_rules[i]);

            g_object_unref(G_OBJECT(imm));

        }

    }

    /* Commentaire */

    text = NULL;

    switch (def->ctype)
    {
        case FCT_PLAIN:
            text = strdup(_(def->comment.plain));
            break;

        case FCT_SWITCH:

            imm = G_IMM_OPERAND(g_arch_instruction_get_operand(instr, 0));
            raw = g_imm_operand_get_raw_value(imm);
            g_object_unref(G_OBJECT(imm));

            for (i = 0; i < def->comment.ccount; i++)
            {
                if (def->comment.choices[i].is_range)
                {
                    if (raw < def->comment.choices[i].lower)
                        continue;
                    if (raw > def->comment.choices[i].upper)
                        continue;
                }

                else if (raw != def->comment.choices[i].fixed)
                    continue;

                text = strnadd(text, _(def->comment.choices[i].desc), strlen(_(def->comment.choices[i].desc)));
                break;

            }

            if (text == NULL)
            {
                assert(i == def->comment.ccount);
                text = strdup(_(def->comment.def_choice));
            }

            break;

        case FCT_MULTI:

            for (i = 0; i < def->comment.pcount; i++)
            {
                part = &def->comment.parts[i];

                if (part->is_static)
                {
                    if (part->avoid_i18n)
                        text = strnadd(text, part->static_text, strlen(part->static_text));
                    else
                        text = strnadd(text, _(part->static_text), strlen(_(part->static_text)));
                }
                else
                {
                    if (part->avoid_i18n)
                        text = strnadd(text, part->dynamic_text, strlen(part->dynamic_text));
                    else
                        text = strnadd(text, _(part->dynamic_text), strlen(_(part->dynamic_text)));
                }

            }

            break;

    }

    addr = get_mrange_addr(g_arch_instruction_get_range(instr));

    comment = g_db_comment_new(addr, CET_INLINED, BLF_HAS_CODE, text);
    g_db_item_add_flag(G_DB_ITEM(comment), DIF_VOLATILE);

    free(text);

    /* Insertions */

    inserted = g_preload_info_add_instruction(info, instr);

    if (inserted)
        g_preload_info_add_comment(info, comment);

    else
        g_object_unref(G_OBJECT(comment));

 pfd_exit:

    g_object_unref(G_OBJECT(content));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : defs   = liste de définitions à traiter.                     *
*                count  = taille de cette liste.                              *
*                format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture pour les données.                   *
*                data   = infos complémentaires éventuellement fournies.      *
*                                                                             *
*  Description : Lance l'interprétation d'une série de définitions de champs. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool parse_field_definitions(const fmt_field_def *defs, size_t count, GBinFormat *format, GPreloadInfo *info, vmpa2t *pos, void *data)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < count && result; i++)
        result = parse_field_definition(defs + i, format, info, pos, data);

    return result;

}
