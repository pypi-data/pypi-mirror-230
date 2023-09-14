
/* Chrysalide - Outil d'analyse de fichiers binaires
 * program.c - annotation des en-têtes de programme de binaires ELF
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#include "program.h"


#include <string.h>


#include <i18n.h>
#include <common/cpp.h>
#include <common/extstr.h>
#include <plugins/elf/elf-int.h>
#include <plugins/fmtp/parser.h>



/* Définition des champs */

static field_desc_switch _elf_prgm_types[] = {

    { .fixed = PT_NULL,         .desc = __("Segment type: unused") },
    { .fixed = PT_LOAD,         .desc = __("Segment type: loadable program segment") },
    { .fixed = PT_DYNAMIC,      .desc = __("Segment type: dynamic linking information") },
    { .fixed = PT_INTERP,       .desc = __("Segment type: program interpreter") },
    { .fixed = PT_NOTE,         .desc = __("Segment type: auxiliary information") },
    { .fixed = PT_SHLIB,        .desc = __("Segment type: reserved") },
    { .fixed = PT_PHDR,         .desc = __("Segment type: entry for header table itself") },
    { .fixed = PT_TLS,          .desc = __("Segment type: thread-local storage segment") },
    { .fixed = PT_GNU_EH_FRAME, .desc = __("Segment type: GCC .eh_frame_hdr segment") },
    { .fixed = PT_GNU_STACK,    .desc = __("Segment type: indicates stack executability") },
    { .fixed = PT_GNU_RELRO,    .desc = __("Segment type: read-only after relocation") },
    { .fixed = PT_SUNWSTACK,    .desc = __("Segment type: Sun Stack segment") },
    { .lower = PT_LOSUNW, .upper = PT_HISUNW, .desc = __("Segment type: Sun specific segment") },
    { .lower = PT_LOOS,   .upper = PT_HIOS,   .desc = __("Segment type: OS-specific") },
    { .lower = PT_LOPROC, .upper = PT_HIPROC, .desc = __("Segment type: processor-specific") }

};

static fmt_field_def _elf_phdr_base[] = {

    {
        .name = "p_type",

        .size = MDS_32_BITS,
        .repeat = 1,

        SWITCH_COMMENT(_elf_prgm_types, __("Segment type: unknown"))

    }

};

static fmt_field_def _elf_phdr_32b_a[] = {

    {
        .name = "p_offset",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment file offset"))

    },

    {
        .name = "p_vaddr",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment virtual address"))

    },

    {
        .name = "p_paddr",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment physical address"))

    },

    {
        .name = "p_filesz",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment size in file"))

    },

    {
        .name = "p_memsz",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment size in memory"))

    }

};

static fmt_field_def _elf_phdr_32b_b[] = {

    {
        .name = "p_align",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment alignment"))

    }

};

static fmt_field_def _elf_phdr_64b[] = {

    {
        .name = "p_offset",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment file offset"))

    },

    {
        .name = "p_vaddr",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment virtual address"))

    },

    {
        .name = "p_paddr",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment physical address"))

    },

    {
        .name = "p_filesz",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment size in file"))

    },

    {
        .name = "p_memsz",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment size in memory"))

    },

    {
        .name = "p_align",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Segment alignment"))

    }

};



/* Charge tous les symboles liés à un en-tête de programme ELF. */
static bool annotate_elf_program_header(GElfFormat *, GPreloadInfo *, SourceEndian, vmpa2t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                endian = boutisme présentement utilisé.                      *
*                pos    = tête de lecture à déplacer. [OUT]                   *
*                                                                             *
*  Description : Charge tous les symboles liés à un en-tête de programme ELF. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_elf_program_header(GElfFormat *format, GPreloadInfo *info, SourceEndian endian, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    elf_phdr phdr;                          /* En-tête de programme ELF    */
    fmt_field_def flags_field;              /* Définition des drapeaux     */
    char *rights;                           /* Reconstruction dynamique    */
    comment_part parts[2];                  /* Mise en place des parties   */
    GBinFormat *bformat;                    /* Autre version du format     */

    result = read_elf_program_header(format, get_phy_addr(pos), &phdr);

    if (!result)
        goto aeph_exit;

    /* Préparation de la partie des drapeaux */

    memset(&flags_field, 0, sizeof(flags_field));

    flags_field.name = "p_flags";

    flags_field.size = MDS_32_BITS;
    flags_field.repeat = 1;

    rights = NULL;

    if (ELF_PHDR(format, phdr, p_flags) & PF_R)
        rights = stradd(rights, "R");

    if (ELF_PHDR(format, phdr, p_flags) & PF_W)
        rights = stradd(rights, "W");

    if (ELF_PHDR(format, phdr, p_flags) & PF_X)
        rights = stradd(rights, "X");

    if (ELF_PHDR(format, phdr, p_flags) & PF_MASKOS)
        rights = stradd(rights, "o");

    if (ELF_PHDR(format, phdr, p_flags) & PF_MASKPROC)
        rights = stradd(rights, "p");

    if (rights == NULL)
    {
        flags_field.ctype = FCT_PLAIN;
        flags_field.comment.plain = __("Segment flags: none");
    }
    else
    {
        parts[0].is_static = true;
        parts[0].avoid_i18n = false;
        parts[0].static_text = __("Segment flags: ");

        parts[1].is_static = false;
        parts[1].avoid_i18n = true;
        parts[1].dynamic_text = rights;

        flags_field.ctype = FCT_MULTI;
        flags_field.comment.parts = parts;
        flags_field.comment.pcount = ARRAY_SIZE(parts);

    }

    /* Interprétation générale */

    bformat = G_BIN_FORMAT(format);

    result = parse_field_definitions(PARSING_DEFS(_elf_phdr_base), bformat, info, pos, NULL);

    if (format->is_32b)
    {
        if (result)
            result = parse_field_definitions(PARSING_DEFS(_elf_phdr_32b_a), bformat, info, pos, NULL);

        if (result)
            result = parse_field_definitions(&flags_field, 1, bformat, info, pos, NULL);

        if (result)
            result = parse_field_definitions(PARSING_DEFS(_elf_phdr_32b_b), bformat, info, pos, NULL);

    }
    else
    {

        if (result)
            result = parse_field_definitions(&flags_field, 1, bformat, info, pos, NULL);

        if (result)
            result = parse_field_definitions(PARSING_DEFS(_elf_phdr_64b), bformat, info, pos, NULL);

    }

 aeph_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge tous les symboles liés aux en-têtes de programme ELF. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_elf_program_header_table(GElfFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const elf_header *header;               /* En-tête principale          */
    SourceEndian endian;                    /* Boutisme utilisé            */
    phys_t offset;                          /* Tête de lecture du bbinaire */
    vmpa2t pos;                             /* Localisation des symboles   */
    uint16_t e_phnum;                       /* Nombre d'éléments 'Program' */
    activity_id_t msg;                      /* Message de progression      */
    uint16_t i;                             /* Boucle de parcours          */

    result = true;

    header = g_elf_format_get_header(format);
    endian = g_binary_format_get_endianness(G_BIN_FORMAT(format));

    offset = ELF_HDR(format, *header, e_phoff);

    if (!g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), offset, &pos))
        return false;

    e_phnum = ELF_HDR(format, *header, e_phnum);

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Elf program headers..."), e_phnum);

    for (i = 0; i < e_phnum && result; i++)
    {
        result = annotate_elf_program_header(format, info, endian, &pos);

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

    return result;

}
