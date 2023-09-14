
/* Chrysalide - Outil d'analyse de fichiers binaires
 * code.c - annotation des éléments de code Dalvik
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


#include "code.h"


#include <plugins/dex/dex_def.h>
#include <plugins/fmtp/parser.h>



/* Définition des champs */

typedef struct _code_item_data
{
    uint16_t tries_size;                    /* Nombre de gestionnaires     */
    uint32_t insns_size;                    /* Nombre d'instructions       */

} code_item_data;

/* Récupère le nombre de couvertures pour exceptions. */
static bool get_code_tries_size_value(const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, code_item_data *);

/* Récupère le nombre de blocs d'instructions. */
static bool get_code_insns_size_value(const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, code_item_data *);

/* Récupère le nombre d'éléments d'une liste de couvertures. */
static bool get_encoded_catch_handler_list_size_value(const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, uleb128_t *);

/* Récupère le nombre d'exécptions gérées dans une couverture. */
static bool get_encoded_catch_handler_size_value(const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, leb128_t *);


static fmt_field_def _dex_code_item[] = {

    {
        .name = "registers_size",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of registers used by this code"))

    },

    {
        .name = "ins_size",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of words of incoming arguments to the method that this code is for"))

    },

    {
        .name = "outs_size",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of words of outgoing argument space required by this code for method invocation"))

    },

    {
        .name = "tries_size",

        .get_value = (get_fdef_value_cb)get_code_tries_size_value,

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of try_items for this instance"))

    },

    {
        .name = "debug_info_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the debug info sequence for this code"))

    },

    {
        .name = "insns_size",

        .get_value = (get_fdef_value_cb)get_code_insns_size_value,

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of the instructions list, in 16-bit code units"))

    }

};

static fmt_field_def _dex_code_item_padding[] = {

    {
        .name = "padding",

        .size = MDS_16_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Padding"))

    }

};

static fmt_field_def _dex_try_item[] = {

    {
        .name = "start_addr",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Start address of the block of code covered by this entry"))

    },

    {
        .name = "insn_count",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of 16-bit code units covered by this entry"))

    },

    {
        .name = "handler_off",

        .size = MDS_16_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the encoded_catch_handler for this entry"))

    }

};

static fmt_field_def _dex_encoded_catch_handler_list[] = {

    {
        .name = "size",

        .get_value = (get_fdef_value_cb)get_encoded_catch_handler_list_size_value,

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of the list, in entries"))

    }

};

static fmt_field_def _dex_encoded_catch_handler[] = {

    {
        .name = "size",

        .get_value = (get_fdef_value_cb)get_encoded_catch_handler_size_value,

        .is_leb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of static fields defined in this item"))

    }

};

static fmt_field_def _dex_encoded_catch_handler_all[] = {

    {
        .name = "catch_all_addr",

        .is_uleb128 = true,

        PLAIN_COMMENT(__("Bytecode address of the catch-all handler"))

    }

};

static fmt_field_def _dex_encoded_type_addr_pair[] = {

    {
        .name = "type_idx",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the type of the exception to catch"))

    },

    {
        .name = "addr",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Bytecode address of the associated exception handler"))

    }

};



/* Commente les définitions d'une protection contre exceptions. */
static bool annotate_dex_try_item(const GDexFormat *, GPreloadInfo *, vmpa2t *);

/*Commente les définitions des listes de gestion d'exceptions. */
static bool annotate_dex_encoded_catch_handler_list(const GDexFormat *, GPreloadInfo *, vmpa2t *);

/* Commente les définitions d'une prise en compte d'exceptions. */
static bool annotate_dex_encoded_catch_handler(const GDexFormat *, GPreloadInfo *, vmpa2t *);

/* Commente les définitions des gestions d'exceptions par type. */
static bool annotate_dex_encoded_type_addr_pair(const GDexFormat *, GPreloadInfo *, vmpa2t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : def     = définition à l'origine de l'appel.                 *
*                content = contenu binaire à venir lire.                      *
*                pos     = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                data    = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Récupère le nombre de couvertures pour exceptions.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool get_code_tries_size_value(const fmt_field_def *def, GBinContent *content, vmpa2t *pos, SourceEndian endian, code_item_data *data)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_u16(content, pos, endian, &data->tries_size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : def     = définition à l'origine de l'appel.                 *
*                content = contenu binaire à venir lire.                      *
*                pos     = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                data    = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Récupère le nombre de blocs d'instructions.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool get_code_insns_size_value(const fmt_field_def *def, GBinContent *content, vmpa2t *pos, SourceEndian endian, code_item_data *data)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_u32(content, pos, endian, &data->insns_size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : def     = définition à l'origine de l'appel.                 *
*                content = contenu binaire à venir lire.                      *
*                pos     = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                size    = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Récupère le nombre d'éléments d'une liste de couvertures.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool get_encoded_catch_handler_list_size_value(const fmt_field_def *def, GBinContent *content, vmpa2t *pos, SourceEndian endian, uleb128_t *size)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_uleb128(content, pos, size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : def     = définition à l'origine de l'appel.                 *
*                content = contenu binaire à venir lire.                      *
*                pos     = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                size    = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Récupère le nombre d'exécptions gérées dans une couverture.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool get_encoded_catch_handler_size_value(const fmt_field_def *def, GBinContent *content, vmpa2t *pos, SourceEndian endian, leb128_t *size)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_leb128(content, pos, size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                                                                             *
*  Description : Commente les définitions d'un corps de méthode.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_code_item(const GDexFormat *format, GPreloadInfo *info, uleb128_t offset)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    code_item_data data;                    /* Valeurs brutes lues         */
    uint16_t i;                             /* Boucle de parcours          */

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), offset, &pos);

    if (!result)
        goto adci_exit;

    result = parse_field_definitions(PARSING_DEFS(_dex_code_item), G_BIN_FORMAT(format), info, &pos, &data);

    if (!result)
        goto adci_exit;

    /* insns */

    advance_vmpa(&pos, data.insns_size * 2);

    /* padding */

    if (data.insns_size % 2 != 0)
        result = parse_field_definitions(PARSING_DEFS(_dex_code_item_padding),
                                         G_BIN_FORMAT(format), info, &pos, NULL);

    /* tries */

    for (i = 0; i < data.tries_size && result; i++)
        result = annotate_dex_try_item(format, info, &pos);

    if (data.tries_size > 0 && result)
        result = annotate_dex_encoded_catch_handler_list(format, info, &pos);

 adci_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture pour les symboles.                  *
*                                                                             *
*  Description : Commente les définitions d'une protection contre exceptions. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_try_item(const GDexFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = parse_field_definitions(PARSING_DEFS(_dex_try_item), G_BIN_FORMAT(format), info, pos, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture physique des symboles.              *
*                                                                             *
*  Description : Commente les définitions des listes de gestion d'exceptions. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_encoded_catch_handler_list(const GDexFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t size;                         /* Nombre d'entrées            */
    uleb128_t i;                            /* Boucle de parcours          */

    result = parse_field_definitions(PARSING_DEFS(_dex_encoded_catch_handler_list),
                                     G_BIN_FORMAT(format), info, pos, &size);

    for (i = 0; i < size && result; i++)
        result = annotate_dex_encoded_catch_handler(format, info, pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture physique des symboles.              *
*                                                                             *
*  Description : Commente les définitions d'une prise en compte d'exceptions. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_encoded_catch_handler(const GDexFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    leb128_t size;                          /* Nombre de gestionnaires     */
    bool has_catch_all;                     /* Gestion par défaut ?        */
    uleb128_t i;                            /* Boucle de parcours          */

    result = parse_field_definitions(PARSING_DEFS(_dex_encoded_catch_handler),
                                     G_BIN_FORMAT(format), info, pos, &size);

    if (!result)
        goto adech_exit;

    has_catch_all = (size <= 0);

    if (size < 0)
        size *= -1;

    /* handlers */

    for (i = 0; i < size && result; i++)
        result = annotate_dex_encoded_type_addr_pair(format, info, pos);

    /* catch_all_addr */

    if (result && has_catch_all)
        result = parse_field_definitions(PARSING_DEFS(_dex_encoded_catch_handler_all),
                                         G_BIN_FORMAT(format), info, pos, &size);

 adech_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture des symboles.                       *
*                                                                             *
*  Description : Commente les définitions des gestions d'exceptions par type. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_encoded_type_addr_pair(const GDexFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = parse_field_definitions(PARSING_DEFS(_dex_encoded_type_addr_pair),
                                     G_BIN_FORMAT(format), info, pos, NULL);

    return result;

}
