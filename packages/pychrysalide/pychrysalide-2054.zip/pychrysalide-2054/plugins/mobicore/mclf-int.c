
/* Chrysalide - Outil d'analyse de fichiers binaires
 * mclf-int.c - structures internes du format MCLF
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


#include "mclf-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                header = en-tête à déterminer. [OUT]                         *
*                endian = boutisme reconnu dans le format. [OUT]              *
*                                                                             *
*  Description : Procède à la lecture de l'en-tête d'un contenu binaire MCLF. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_mclf_header(GMCLFFormat *format, mclf_header_t *header, SourceEndian endian)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */
    uint32_t tmp;                           /* Espace de transition        */

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_u32(content, &pos, endian, &header->intro.magic);
    result &= g_binary_content_read_u32(content, &pos, endian, &header->intro.version);

    result &= g_binary_content_read_u32(content, &pos, endian, &header->v1.flags);

    result &= g_binary_content_read_u32(content, &pos, endian, &tmp);
    header->v1.mem_type = tmp;

    result &= g_binary_content_read_u32(content, &pos, endian, &tmp);
    header->v1.service_type = tmp;

    result &= g_binary_content_read_u32(content, &pos, endian, &header->v1.num_instances);
    result &= g_binary_content_read_raw(content, &pos, 16, (bin_t *)&header->v1.uuid);

    result &= g_binary_content_read_u32(content, &pos, endian, &tmp);
    header->v1.driver_id = tmp;

    result &= g_binary_content_read_u32(content, &pos, endian, &header->v1.num_threads);

    result &= read_mclf_segment_desc(format, &header->v1.text, &pos, endian);

    result &= read_mclf_segment_desc(format, &header->v1.data, &pos, endian);

    result &= g_binary_content_read_u32(content, &pos, endian, &header->v1.bss_len);
    result &= g_binary_content_read_u32(content, &pos, endian, &header->v1.entry);

    result &= g_binary_content_read_u32(content, &pos, endian, &header->v2.service_version);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                segment = descripteur à déterminer. [OUT]                    *
*                pos     = position de début de lecture. [OUT]                *
*                endian  = boutisme reconnu dans le format. [OUT]             *
*                                                                             *
*  Description : Procède à la lecture d'un descripteur de segment MCLF.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_mclf_segment_desc(GMCLFFormat *format, segment_descriptor_t *segment, vmpa2t *pos, SourceEndian endian)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u32(content, pos, endian, &segment->start);
    result &= g_binary_content_read_u32(content, pos, endian, &segment->len);

    return result;

}
