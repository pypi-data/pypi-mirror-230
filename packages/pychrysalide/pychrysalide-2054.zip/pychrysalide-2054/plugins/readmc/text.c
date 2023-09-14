
/* Chrysalide - Outil d'analyse de fichiers binaires
 * text.c - annotation de l'en-tête du code pour Mobicore
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


#include "text.h"


#include <plugins/fmtp/parser.h>



/* Définition des champs */

static fmt_field_def _mobicore_text_header[] = {

    {
        .name = "version",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Version of the TextHeader structure"))

    },

    {
        .name = "textHeaderLen",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Size of this structure (fixed at compile time)"))

    },

    {
        .name = "requiredFeat",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Features that Mobicore must understand/interprete when loading"))

    },

    {
        .name = "mcLibEntry",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Address for McLib entry"))

    },

    {
        .name = "mcIMD",

        .size = MDS_32_BITS,
        .repeat = 2,

        PLAIN_COMMENT(__("McLib Internal Management Data"))

    },

    {
        .name = "tlApiVers",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("TlApi version used when building trustlet"))

    },

    {
        .name = "drApiVers",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("DrApi version used when building trustlet"))

    },

    {
        .name = "ta_properties",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Address of _TA_Properties in the TA"))

    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture courante. [OUT]                     *
*                                                                             *
*  Description : Charge les symboles d'un en-tête de code pour Mobicore.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_mobicore_text_header(GBinFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = parse_field_definitions(PARSING_DEFS(_mobicore_text_header), format, info, pos, NULL);

    return result;

}
