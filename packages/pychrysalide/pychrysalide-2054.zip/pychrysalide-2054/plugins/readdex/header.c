
/* Chrysalide - Outil d'analyse de fichiers binaires
 * header.c - annotation des en-têtes de binaires DEX
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#include "header.h"


#include <i18n.h>
#include <plugins/dex/dex_def.h>
#include <plugins/fmtp/parser.h>



/* Définition des champs */

static fmt_field_def _dex_header[] = {

    {
        .name = "magic",

        .size = MDS_8_BITS,
        .repeat = DEX_FILE_MAGIC_LEN ,

        DISPLAY_RULES(IOD_CHAR, IOD_CHAR, IOD_CHAR, IOD_HEX, IOD_CHAR, IOD_CHAR, IOD_CHAR, IOD_HEX),

        PLAIN_COMMENT(__("DEX magic number"))

    },

    {
        .name = "checksum",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("adler32 checksum used to detect file corruption"))

    },

    {
        .name = "signature",

        .size = MDS_32_BITS,
        .repeat = 5,

        PLAIN_COMMENT(__("SHA-1 signature used to uniquely identify files"))

    },

    {
        .name = "file_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of the entire file in bytes"))

    },

    {
        .name = "header_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of the header in bytes"))

    },

    {
        .name = "endian_tag",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Endianness tag ; 0x12345678 for little-endian"))

    },

    {
        .name = "link_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of the link section"))

    },

    {
        .name = "link_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the link section"))

    },

    {
        .name = "map_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the map item"))

    },

    {
        .name = "string_ids_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Count of strings in the string identifiers list"))

    },

    {
        .name = "string_ids_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the string identifiers list"))

    },

    {
        .name = "type_ids_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Count of elements in the type identifiers list"))

    },

    {
        .name = "type_ids_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the type identifiers list"))

    },

    {
        .name = "proto_ids_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Count of elements in the prototype identifiers list"))

    },

    {
        .name = "proto_ids_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the prototype identifiers list"))

    },

    {
        .name = "field_ids_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Count of elements in the field identifiers list"))

    },

    {
        .name = "field_ids_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the field identifiers list"))

    },

    {
        .name = "method_ids_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Count of elements in the method identifiers list"))

    },

    {
        .name = "method_ids_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Offset to the method identifiers list"))

    },

    {
        .name = "class_defs_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Count of elements in the class definitions list"))

    },

    {
        .name = "class_defs_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the class definitions list"))

    },

    {
        .name = "data_size",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of data section in bytes"))

    },

    {
        .name = "data_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the start of the data section"))

    }

};


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                                                                             *
*  Description : Charge tous les symboles de l'en-tête DEX.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_header(GDexFormat *format, GPreloadInfo *info)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Tête de lecture des symboles*/

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), 0, &pos);

    if (result)
        result = parse_field_definitions(PARSING_DEFS(_dex_header), G_BIN_FORMAT(format), info, &pos, NULL);

    return result;

}
