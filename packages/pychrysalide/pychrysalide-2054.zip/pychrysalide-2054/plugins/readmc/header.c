
/* Chrysalide - Outil d'analyse de fichiers binaires
 * header.c - annotation des en-têtes de binaires ELF
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include <plugins/fmtp/parser.h>



/* Définition des champs */

/* Récupère la version du format. */
static bool get_mclf_version(const fmt_field_def *, GBinContent *, vmpa2t *, SourceEndian, uint32_t *);


static fmt_field_def _mc_intro[] = {

    {
        .name = "magic",

        .size = MDS_8_BITS,
        .repeat = 4,

        DISPLAY_RULES(IOD_CHAR, IOD_CHAR, IOD_CHAR, IOD_CHAR),

        PLAIN_COMMENT(__("Header magic value"))

    },

    {
        .name = "version",

        .get_value = (get_fdef_value_cb)get_mclf_version,

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Version of the MCLF header structure"))

    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : def     = définition à l'origine de l'appel.                 *
*                content = contenu binaire à venir lire.                      *
*                pos     = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                version = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Récupère la version du format.                               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool get_mclf_version(const fmt_field_def *def, GBinContent *content, vmpa2t *pos, SourceEndian endian, uint32_t *version)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_u32(content, pos, endian, version);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à compléter.           *
*                info    = informations à constituer en avance de phase.      *
*                pos     = tête de lecture courante. [OUT]                    *
*                version = version du format récupérée. [OUT]                 *
*                                                                             *
*  Description : Charge tous les symboles de l'en-tête Mobicore.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_mobicore_header(GBinFormat *format, GPreloadInfo *info, vmpa2t *pos, uint32_t *version)
{
    bool result;                            /* Bilan à retourner           */

    result = parse_field_definitions(PARSING_DEFS(_mc_intro), format, info, pos, version);

    return result;

}
