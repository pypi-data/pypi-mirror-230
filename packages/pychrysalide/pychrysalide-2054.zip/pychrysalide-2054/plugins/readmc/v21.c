
/* Chrysalide - Outil d'analyse de fichiers binaires
 * v21.c - annotation des parties spécifiques à la version 2.1/2.2 de Mobicore
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


#include "v21.h"


#include <plugins/fmtp/parser.h>
#include <plugins/mobicore/mclf-def.h>



/* Définition des champs */

static field_desc_switch _v21_mc_memories[] = {

    { .fixed = MCLF_MEM_TYPE_INTERNAL_PREFERRED, .desc = __("If available use internal memory; otherwise external memory") },
    { .fixed = MCLF_MEM_TYPE_INTERNAL,           .desc = __("Internal memory must be used for executing the service") },
    { .fixed = MCLF_MEM_TYPE_EXTERNAL,           .desc = __("External memory must be used for executing the service") }

};

static field_desc_switch _v21_mc_services[] = {

    { .fixed = SERVICE_TYPE_ILLEGAL,         .desc = __("Service type is invalid") },
    { .fixed = SERVICE_TYPE_DRIVER,          .desc = __("Service is a driver") },
    { .fixed = SERVICE_TYPE_SP_TRUSTLET,     .desc = __("Service is a Trustlet") },
    { .fixed = SERVICE_TYPE_SYSTEM_TRUSTLET, .desc = __("Service is a system Trustlet") },
    { .fixed = SERVICE_TYPE_MIDDLEWARE,      .desc = __("Service is a middleware") }

};

static field_desc_switch _v21_mc_drivers[] = {

    { .fixed = MC_DRV_ID_INVALID,            .desc = "MC_DRV_ID_INVALID" },
    { .fixed = MC_DRV_ID_CRYPTO,             .desc = "MC_DRV_ID_CRYPTO" },
    { .fixed = MC_DRV_ID_LAST_PRE_INSTALLED, .desc = "MC_DRV_ID_LAST_PRE_INSTALLED" },
    { .fixed = TB_DRV_ID_TUI,                .desc = "TB_DRV_ID_TUI" },
    { .fixed = TB_DRV_ID_TPLAY,              .desc = "TB_DRV_ID_TPLAY" }

};

static fmt_field_def _mobicore_v21_header[] = {

    {
        .name = "flags",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Service flags"))

    },

    {
        .name = "memType",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_v21_mc_memories, __("The service must be executed from unknown memory type"))

    },

    {
        .name = "serviceType",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        SWITCH_COMMENT(_v21_mc_services, __("Service is unknown"))

    },

    {
        .name = "numInstances",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of instances which can be run simultaneously"))

    },

    {
        .name = "uuid",

        .size = MDS_32_BITS,
        .repeat = 4,

        PLAIN_COMMENT(__("Loadable service unique identifier (UUID)"))

    },

    {
        .name = "driverId",

        .size = MDS_32_BITS,
        .repeat = 1,

        SWITCH_COMMENT(_v21_mc_drivers, __("Unknown driver identifier"))

    },

    {
        .name = "numThreads",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of threads in a service depending on service type"))

    },

    {
        .name = "text_start",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Text segment: virtual start address"))

    },

    {
        .name = "text_len",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Text segment: length in bytes"))

    },

    {
        .name = "data_start",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Data segment: virtual start address"))

    },

    {
        .name = "data_len",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Data segment: length in bytes"))

    },

    {
        .name = "bssLen",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Length of the BSS segment in bytes"))

    },

    {
        .name = "entry",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Virtual start address of service code"))

    },

    {
        .name = "serviceVersion",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Version of the interface the driver exports"))

    }

};



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture courante. [OUT]                     *
*                                                                             *
*  Description : Charge les symboles d'un en-tête v2.1/2.2 de Mobicore.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_mobicore_v21_header(GBinFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */

    result = parse_field_definitions(PARSING_DEFS(_mobicore_v21_header), format, info, pos, NULL);

    return result;

}
