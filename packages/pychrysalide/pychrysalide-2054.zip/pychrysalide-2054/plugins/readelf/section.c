
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.c - annotation des en-têtes de section de binaires ELF
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


#include "section.h"


#include <string.h>


#include <i18n.h>
#include <common/cpp.h>
#include <common/extstr.h>
#include <plugins/elf/elf-int.h>
#include <plugins/elf/section.h>
#include <plugins/fmtp/parser.h>



/* Définition des champs */

static field_desc_switch _elf_section_types[] = {

    { .fixed = SHT_NULL,           .desc = __("Section type: unused") },
    { .fixed = SHT_PROGBITS,       .desc = __("Section type: program data") },
    { .fixed = SHT_SYMTAB,         .desc = __("Section type: symbol table") },
    { .fixed = SHT_STRTAB,         .desc = __("Section type: string table") },
    { .fixed = SHT_RELA,           .desc = __("Section type: relocation entries with addends") },
    { .fixed = SHT_HASH,           .desc = __("Section type: symbol hash table") },
    { .fixed = SHT_DYNAMIC,        .desc = __("Section type: dynamic linking information") },
    { .fixed = SHT_NOTE,           .desc = __("Section type: notes") },
    { .fixed = SHT_NOBITS,         .desc = __("Section type: program space with no data (bss)") },
    { .fixed = SHT_REL,            .desc = __("Section type: relocation entries, no addends") },
    { .fixed = SHT_SHLIB,          .desc = __("Section type: reserved") },
    { .fixed = SHT_DYNSYM,         .desc = __("Section type: dynamic linker symbol table") },
    { .fixed = SHT_INIT_ARRAY,     .desc = __("Section type: array of constructors") },
    { .fixed = SHT_FINI_ARRAY,     .desc = __("Section type: array of destructors") },
    { .fixed = SHT_PREINIT_ARRAY,  .desc = __("Section type: array of pre-constructors") },
    { .fixed = SHT_GROUP,          .desc = __("Section type: section group") },
    { .fixed = SHT_SYMTAB_SHNDX,   .desc = __("Section type: extended section indeces") },
    { .fixed = SHT_GNU_ATTRIBUTES, .desc = __("Section type: object attributes") },
    { .fixed = SHT_GNU_HASH,       .desc = __("Section type: GNU-style hash table") },
    { .fixed = SHT_GNU_LIBLIST,    .desc = __("Section type: prelink library list") },
    { .fixed = SHT_CHECKSUM,       .desc = __("Section type: checksum for DSO content") },
    { .fixed = SHT_SUNW_move,      .desc = __("Section type: SHT_SUNW_move") },
    { .fixed = SHT_SUNW_COMDAT,    .desc = __("Section type: SHT_SUNW_COMDAT") },
    { .fixed = SHT_SUNW_syminfo,   .desc = __("Section type: SHT_SUNW_syminfo") },
    { .fixed = SHT_GNU_verdef,     .desc = __("Section type: version definition section") },
    { .fixed = SHT_GNU_verneed,    .desc = __("Section type: version needs section") },
    { .fixed = SHT_GNU_versym,     .desc = __("Section type: version symbol table") },
    { .lower = SHT_LOSUNW, .upper = SHT_HISUNW, .desc = __("Section type: Sun-specific") },
    { .lower = SHT_LOOS,   .upper = SHT_HIOS,   .desc = __("Section type: OS-specific") },
    { .lower = SHT_LOPROC, .upper = SHT_HIPROC, .desc = __("Section type: processor-specific") },
    { .lower = SHT_LOUSER, .upper = SHT_HIUSER, .desc = __("Section type: application-specific") }

};

static fmt_field_def _elf_sh_type[] = {

    {
        .name = "sh_type",

        .size = MDS_32_BITS,
        .repeat = 1,

        SWITCH_COMMENT(_elf_section_types, __("Section type: unknown"))

    }

};

static fmt_field_def _elf_shdr_32b[] = {

    {
        .name = "sh_addr",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section virtual addr at execution"))

    },

    {
        .name = "sh_offset",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section file offset"))

    },

    {
        .name = "sh_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Section size in bytes"))

    },

    {
        .name = "sh_link",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Link to another section"))

    },

    {
        .name = "sh_info",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Additional section information"))

    },

    {
        .name = "sh_addralign",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section alignment"))

    },

    {
        .name = "sh_entsize",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Entry size if section holds table"))

    }

};

static fmt_field_def _elf_shdr_64b[] = {

    {
        .name = "sh_addr",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section virtual addr at execution"))

    },

    {
        .name = "sh_offset",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section file offset"))

    },

    {
        .name = "sh_size",

        .size = MDS_64_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Section size in bytes"))

    },

    {
        .name = "sh_link",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Link to another section"))

    },

    {
        .name = "sh_info",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Additional section information"))

    },

    {
        .name = "sh_addralign",

        .size = MDS_64_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Section alignment"))

    },

    {
        .name = "sh_entsize",

        .size = MDS_64_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Entry size if section holds table"))

    }

};



/* Charge tous les symboles liés à un en-tête de section ELF. */
static bool annotate_elf_section_header(GElfFormat *, GPreloadInfo *, SourceEndian, const elf_shdr *, vmpa2t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à compléter.           *
*                info    = informations à constituer en avance de phase.      *
*                endian  = boutisme présentement utilisé.                     *
*                strings = section renvoyant vers des chaînes de caractères.  *
*                pos     = tête de lecture à déplacer. [OUT]                  *
*                                                                             *
*  Description : Charge tous les symboles liés à un en-tête de section ELF.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_elf_section_header(GElfFormat *format, GPreloadInfo *info, SourceEndian endian, const elf_shdr *strings, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    elf_shdr shdr;                          /* En-tête de programme ELF    */
    fmt_field_def name_field;               /* Définition du nom de section*/
    const char *secname;                    /* Nom d'une section analysée  */
    comment_part nparts[2];                 /* Mise en place des parties   */
    fmt_field_def flags_field;              /* Définition des drapeaux     */
    char *rights;                           /* Reconstruction dynamique    */
    comment_part fparts[2];                 /* Mise en place des parties   */
    GBinFormat *bformat;                    /* Autre version du format     */

    result = read_elf_section_header(format, get_phy_addr(pos), &shdr);

    if (!result)
        goto aesh_exit;

    /* Préparation de la partie nominative */

    memset(&name_field, 0, sizeof(name_field));

    name_field.name = "sh_name";

    name_field.size = MDS_32_BITS;
    name_field.repeat = 1;

    name_field.has_display_rules = true;
    name_field.disp_rules = (ImmOperandDisplay []) { IOD_DEC };
    name_field.disp_count = 1;

    secname = extract_name_from_elf_string_section(format, strings,
                                                   ELF_SHDR(format, shdr, sh_name));

    if (secname == NULL)
    {
        name_field.ctype = FCT_PLAIN;
        name_field.comment.plain = __("Section name: <invalid>");
    }
    else
    {
        nparts[0].is_static = true;
        nparts[0].avoid_i18n = false;
        nparts[0].static_text = __("Segment name: ");

        nparts[1].is_static = true;
        nparts[1].avoid_i18n = true;
        nparts[1].static_text = secname;

        name_field.ctype = FCT_MULTI;
        name_field.comment.parts = nparts;
        name_field.comment.pcount = ARRAY_SIZE(nparts);

    }

    /* Préparation de la partie des drapeaux */

    memset(&flags_field, 0, sizeof(flags_field));

    flags_field.name = "sh_flags";

    flags_field.repeat = 1;

    rights = NULL;

    if (ELF_SHDR(format, shdr, sh_type) & SHF_WRITE)
        rights = stradd(rights, "W");

    if (ELF_SHDR(format, shdr, sh_type) & SHF_ALLOC)
        rights = stradd(rights, "A");

    if (ELF_SHDR(format, shdr, sh_type) & SHF_EXECINSTR)
        rights = stradd(rights, "X");

    if (ELF_SHDR(format, shdr, sh_type) & SHF_MERGE)
        rights = stradd(rights, "M");

    if (ELF_SHDR(format, shdr, sh_type) & SHF_LINK_ORDER)
        rights = stradd(rights, "L");

    if (ELF_SHDR(format, shdr, sh_type) & SHF_TLS)
        rights = stradd(rights, "T");

    if (rights == NULL)
    {
        flags_field.ctype = FCT_PLAIN;
        flags_field.comment.plain = __("Section flags: none");
    }
    else
    {
        fparts[0].is_static = true;
        fparts[0].avoid_i18n = false;
        fparts[0].static_text = __("Section flags: ");

        fparts[1].is_static = false;
        fparts[1].avoid_i18n = true;
        fparts[1].dynamic_text = rights;

        flags_field.ctype = FCT_MULTI;
        flags_field.comment.parts = fparts;
        flags_field.comment.pcount = ARRAY_SIZE(fparts);

    }

    /* Interprétation générale */

    bformat = G_BIN_FORMAT(format);

    result = parse_field_definitions(&name_field, 1, bformat, info, pos, NULL);

    if (result)
        result = parse_field_definitions(PARSING_DEFS(_elf_sh_type), bformat, info, pos, NULL);

    if (format->is_32b)
    {
        if (result)
        {
            flags_field.size = MDS_32_BITS;
            result = parse_field_definitions(&flags_field, 1, bformat, info, pos, NULL);
        }

        if (result)
            result = parse_field_definitions(PARSING_DEFS(_elf_shdr_32b), bformat, info, pos, NULL);

    }
    else
    {
        if (result)
        {
            flags_field.size = MDS_64_BITS;
            result = parse_field_definitions(&flags_field, 1, bformat, info, pos, NULL);
        }

        if (result)
            result = parse_field_definitions(PARSING_DEFS(_elf_shdr_64b), bformat, info, pos, NULL);

    }

 aesh_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge tous les symboles liés aux en-têtes de section ELF.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_elf_section_header_table(GElfFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const elf_header *header;               /* En-tête principale          */
    SourceEndian endian;                    /* Boutisme utilisé            */
    elf_shdr strings;                       /* Section des descriptions    */
    off_t offset;                           /* Tête de lecture du binaire  */
    vmpa2t pos;                             /* Localisation des symboles   */
    uint16_t e_shnum;                       /* Nombre d'éléments 'Program' */
    activity_id_t msg;                      /* Message de progression      */
    uint16_t i;                             /* Boucle de parcours          */

    result = true;

    header = g_elf_format_get_header(format);
    endian = g_binary_format_get_endianness(G_BIN_FORMAT(format));

    if (!find_elf_section_by_index(format, ELF_HDR(format, *header, e_shstrndx), &strings))
        return false;

    offset = ELF_HDR(format, *header, e_shoff);

    if (!g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), offset, &pos))
        init_vmpa(&pos, offset, VMPA_NO_VIRTUAL);

    e_shnum = ELF_HDR(format, *header, e_shnum);

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Elf section headers..."), e_shnum);

    for (i = 0; i < e_shnum && result; i++)
    {
        result = annotate_elf_section_header(format, info, endian, &strings, &pos);

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

    return result;

}
