
/* Chrysalide - Outil d'analyse de fichiers binaires
 * v23.c - annotation des parties spécifiques à la version 2.3 de Mobicore
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


#include "v23.h"


#include <plugins/fmtp/parser.h>



/* Définition des champs */

static fmt_field_def _mobicore_v23_header[] = {

    {
        .name = "permittedSuid_id",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("SUID (1/2) allowed to execute binary: Silicon Provider identifier"))

    },

    {
        .name = "permittedSuid_data",

        .size = MDS_32_BITS,
        .repeat = 3,

        PLAIN_COMMENT(__("SUID (2/2) allowed to execute binary: platform specific device identifier"))

    },

    {
        .name = "permittedHwCfg",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Hardware configuration allowed to execute binary"))

    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture courante. [OUT]                     *
*                                                                             *
*  Description : Charge les symboles d'un en-tête v2.3 de Mobicore.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_mobicore_v23_header(GBinFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = parse_field_definitions(PARSING_DEFS(_mobicore_v23_header), format, info, pos, NULL);

    return result;

}
