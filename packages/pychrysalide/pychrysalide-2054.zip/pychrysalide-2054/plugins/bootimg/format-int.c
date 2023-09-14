
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format-int.c - structures internes du format BOOT.img
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "format-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                header = en-tête à déterminer. [OUT]                         *
*                                                                             *
*  Description : Procède à la lecture de l'entête d'une image BOOT.img.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_bootimg_header(GBootImgFormat *format, boot_img_hdr *header)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    init_vmpa(&pos, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &pos, BOOT_MAGIC_SIZE, (bin_t *)header->magic);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->kernel_size);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->kernel_addr);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->ramdisk_size);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->ramdisk_addr);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->second_size);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->second_addr);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->tags_addr);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->page_size);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->header_version);

    if (result)
        result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->os_version);

    if (result)
        result = g_binary_content_read_raw(content, &pos, BOOT_NAME_SIZE, (bin_t *)header->name);

    if (result)
        result = g_binary_content_read_raw(content, &pos, BOOT_ARGS_SIZE, (bin_t *)header->cmdline);

    if (result)
        result = g_binary_content_read_raw(content, &pos, 8, (bin_t *)header->id);

    if (result)
        result = g_binary_content_read_raw(content, &pos, BOOT_EXTRA_ARGS_SIZE, (bin_t *)header->extra_cmdline);

    if (result && header->header_version == 1)
    {
        if (result)
            result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->recovery_dtbo_size);

        if (result)
            result = g_binary_content_read_u64(content, &pos, SRE_LITTLE, &header->recovery_dtbo_offset);

        if (result)
            result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->header_size);

    }

    g_object_unref(G_OBJECT(content));

    return result;

}
