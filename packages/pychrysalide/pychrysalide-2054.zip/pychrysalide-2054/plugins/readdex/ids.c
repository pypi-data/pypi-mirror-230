
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ids.c - annotation des références aux chaînes de caractères et identifiants
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


#include "ids.h"


#include <malloc.h>
#include <stdio.h>


#include <i18n.h>
#include <arch/instructions/raw.h>
#include <format/known.h>
#include <format/symbol.h>
#include <plugins/dex/dex_def.h>
#include <plugins/fmtp/parser.h>



/* Définition des champs */


/* Récupère la taille d'une chaîne de caractères. */
static bool get_dex_string_length_value(const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, uleb128_t *);


static fmt_field_def _dex_string_ids_length[] = {

    {
        .name = "length",

        .get_value = (get_fdef_value_cb)get_dex_string_length_value,

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("String length"))

    }

};

static fmt_field_def _dex_type_ids[] = {

    {
        .name = "descriptor_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the descriptor string of this type"))

    }

};

static fmt_field_def _dex_proto_ids[] = {

    {
        .name = "shorty_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the short-form descriptor string of this prototype"))

    },

    {
        .name = "return_type_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the return type of this prototype"))

    },

    {
        .name = "parameters_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the list of parameter types for this prototype"))

    }

};

static fmt_field_def _dex_field_ids[] = {

    {
        .name = "class_idx",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the definer of this field"))

    },

    {
        .name = "type_idx",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the type of this field"))

    },

    {
        .name = "name_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the name of this field"))

    }

};

static fmt_field_def _dex_method_ids[] = {

    {
        .name = "class_idx",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the definer of this field"))

    },

    {
        .name = "proto_idx",

        .size = MDS_16_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the prototype of this method"))

    },

    {
        .name = "name_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the name of this method"))

    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : def     = définition à l'origine de l'appel.                 *
*                content = contenu binaire à venir lire.                      *
*                pos     = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                data    = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Récupère la taille d'une chaîne de caractères.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool get_dex_string_length_value(const fmt_field_def *def, GBinContent *content, vmpa2t *pos, SourceEndian endian, uleb128_t *length)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_uleb128(content, pos, length);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Commente les définitions des chaînes de caractères.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_string_ids(const GDexFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    const dex_header *header;               /* En-tête principale          */
    SourceEndian endian;                    /* Boutisme utilisé            */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *bformat;                    /* Autre version du format     */
    uint32_t i;                             /* Boucle de parcours          */
    fmt_field_def field;                    /* Définition de position      */
    comment_part parts[2];                  /* Mise en place des parties   */
    phys_t loc;                             /* Localisation physique       */
    vmpa2t item_pos;                        /* Position d'un élément       */
    uleb128_t length;                       /* Taille de la chaîne en cours*/
    GArchInstruction *instr;                /* Instruction décodée         */

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    header = g_dex_format_get_header(format);
    endian = g_binary_format_get_endianness(G_BIN_FORMAT(format));

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), header->string_ids_off, &pos);

    if (!result)
        goto adsi_exit;

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Dex strings..."),
                                        header->string_ids_size);

    bformat = G_BIN_FORMAT(format);

    bool get_string_offset_value(const fmt_field_def *d, GBinContent *c, vmpa2t *p, SourceEndian e, phys_t *val)
    {
        bool status;                        /* Bilan à retourner           */
        uint32_t offset;                    /* Position trouvée            */

        status = g_binary_content_read_u32(c, p, e, &offset);

        if (status)
            *val = offset;

        return status;

    }

    for (i = 0; i < header->string_ids_size && result; i++)
    {
        /* Saut vers la définition */

        memset(&field, 0, sizeof(field));

        field.name = "p_flags";

        field.get_value = (get_fdef_value_cb)get_string_offset_value;

        field.size = MDS_32_BITS;
        field.repeat = 1;

        parts[0].is_static = true;
        parts[0].avoid_i18n = false;
        parts[0].static_text = __("Offset for string item #");

        parts[1].is_static = false;
        parts[1].avoid_i18n = true;
        asprintf(&parts[1].dynamic_text, "%u/%u", i, header->string_ids_size - 1);

        field.ctype = FCT_MULTI;
        field.comment.parts = parts;
        field.comment.pcount = ARRAY_SIZE(parts);

        result = parse_field_definitions(&field, 1, bformat, info, &pos, &loc);

        if (!result)
            break;

        /* Description de la chaîne : taille */

        if (!g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), loc, &item_pos))
            continue;

        result = parse_field_definitions(PARSING_DEFS(_dex_string_ids_length), bformat, info, &item_pos, &length);

        /* Description de la chaîne : contenu */

        if (result && length > 0)
        {
            instr = g_raw_instruction_new_array(content, MDS_8_BITS, length, &item_pos, endian);

            if (instr != NULL)
            {
                g_raw_instruction_mark_as_string(G_RAW_INSTRUCTION(instr), true);

                g_preload_info_add_instruction(info, instr);

            }

        }

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

    g_object_unref(G_OBJECT(content));

 adsi_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Commente les définitions des identifiants de types.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_type_ids(const GDexFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const dex_header *header;               /* En-tête principale          */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *bformat;                    /* Autre version du format     */
    uint32_t i;                             /* Boucle de parcours          */

    header = g_dex_format_get_header(format);

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), header->type_ids_off, &pos);

    if (!result)
        goto adti_exit;

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Dex types..."),
                                        header->type_ids_size);

    bformat = G_BIN_FORMAT(format);

    for (i = 0; i < header->type_ids_size && result; i++)
    {
        result = parse_field_definitions(PARSING_DEFS(_dex_type_ids), bformat, info, &pos, NULL);

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

 adti_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Commente les définitions des identifiants de prototypes.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_proto_ids(const GDexFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const dex_header *header;               /* En-tête principale          */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *bformat;                    /* Autre version du format     */
    uint32_t i;                             /* Boucle de parcours          */

    header = g_dex_format_get_header(format);

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), header->proto_ids_off, &pos);

    if (!result)
        goto adpi_exit;

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Dex prototypes..."),
                                        header->proto_ids_size);

    bformat = G_BIN_FORMAT(format);

    for (i = 0; i < header->proto_ids_size && result; i++)
    {
        result = parse_field_definitions(PARSING_DEFS(_dex_proto_ids), bformat, info, &pos, NULL);

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

 adpi_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Commente les définitions des identifiants de champs.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_field_ids(const GDexFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const dex_header *header;               /* En-tête principale          */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *bformat;                    /* Autre version du format     */
    uint32_t i;                             /* Boucle de parcours          */

    header = g_dex_format_get_header(format);

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), header->field_ids_off, &pos);

    if (!result)
        goto adfi_exit;

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Dex fields..."),
                                        header->field_ids_size);

    bformat = G_BIN_FORMAT(format);

    for (i = 0; i < header->field_ids_size && result; i++)
    {
        result = parse_field_definitions(PARSING_DEFS(_dex_field_ids), bformat, info, &pos, NULL);

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

 adfi_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Commente les définitions des identifiants de méthodes.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_method_ids(const GDexFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const dex_header *header;               /* En-tête principale          */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *bformat;                    /* Autre version du format     */
    uint32_t i;                             /* Boucle de parcours          */

    header = g_dex_format_get_header(format);

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), header->method_ids_off, &pos);

    if (!result)
        goto admi_exit;

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Dex methods..."),
                                        header->method_ids_size);

    bformat = G_BIN_FORMAT(format);

    for (i = 0; i < header->method_ids_size && result; i++)
    {
        result = parse_field_definitions(PARSING_DEFS(_dex_method_ids), bformat, info, &pos, NULL);

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

 admi_exit:

    return result;

}
