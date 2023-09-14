
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pe-int.c - structures internes du format Portable Executable
 *
 * Copyright (C) 2010-2017 Cyrille Bagard
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


#include "pe-int.h"


#include <malloc.h>
#include <string.h>

#include <i18n.h>
#include <common/endianness.h>
#include <core/logs.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                header = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un en-tête de programme DOS.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dos_image_header(const GPeFormat *format, image_dos_header *header)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, 0, VMPA_NO_VIRTUAL);

    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_magic);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_cblp);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_cp);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_crlc);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_cparhdr);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_minalloc);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_maxalloc);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_ss);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_sp);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_csum);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_ip);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_cs);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_lfarlc);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_ovno);

    for (i = 0; i < 4 && result; i++)
        result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_res[i]);

    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_oemid);
    if (result) result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_oeminfo);

    for (i = 0; i < 10 && result; i++)
        result = g_binary_content_read_u16(content, &pos, SRE_LITTLE, &header->e_res2[i]);

    if (result) result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->e_lfanew);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                header = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un en-tête de programme PE (1).       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_pe_file_header(const GPeFormat *format, vmpa2t *pos, image_file_header *header)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &header->machine);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &header->number_of_sections);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->time_date_stamp);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->pointer_to_symbol_table);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->number_of_symbols);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &header->size_of_optional_header);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &header->characteristics);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                header = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un en-tête de programme PE (2).       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_pe_optional_header(const GPeFormat *format, vmpa2t *pos, image_optional_header *header)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    image_optional_header_32 *hdr32;        /* Version 32 bits             */
    image_optional_header_64 *hdr64;        /* Version 64 bits             */
    image_data_directory *directories;      /* Répertoires à charger       */
    uint32_t *number_of_rva_and_sizes;      /* Quantité de ces répertoires */
    uint32_t i;                             /* Boucle de parcours          */

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &header->header_32.magic);
    if (!result) goto exit;

    ((GPeFormat *)format)->loaded = true;

    if (g_pe_format_get_is_32b(format))
    {
        hdr32 = &header->header_32;

        if (result) result = g_binary_content_read_u8(content, pos, &hdr32->major_linker_version);
        if (result) result = g_binary_content_read_u8(content, pos, &hdr32->minor_linker_version);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_code);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_initialized_data);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_uninitialized_data);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->address_of_entry_point);

        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->base_of_code);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->base_of_data);

        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->image_base);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->section_alignment);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->file_alignment);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->major_operating_system_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->minor_operating_system_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->major_image_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->minor_image_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->major_subsystem_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->minor_subsystem_version);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->win32_version_value);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_image);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_headers);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->checksum);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->subsystem);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr32->dll_characteristics);

        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_stack_reserve);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_stack_commit);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_heap_reserve);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->size_of_heap_commit);

        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->loader_flags);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr32->number_of_rva_and_sizes);

        directories = hdr32->data_directory;
        number_of_rva_and_sizes = &hdr32->number_of_rva_and_sizes;

    }
    else
    {
        hdr64 = &header->header_64;

        if (result) result = g_binary_content_read_u8(content, pos, &hdr64->major_linker_version);
        if (result) result = g_binary_content_read_u8(content, pos, &hdr64->minor_linker_version);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->size_of_code);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->size_of_initialized_data);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->size_of_uninitialized_data);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->address_of_entry_point);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->base_of_code);

        if (result) result = g_binary_content_read_u64(content, pos, SRE_LITTLE, &hdr64->image_base);

        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->section_alignment);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->file_alignment);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->major_operating_system_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->minor_operating_system_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->major_image_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->minor_image_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->major_subsystem_version);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->minor_subsystem_version);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->win32_version_value);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->size_of_image);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->size_of_headers);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->checksum);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->subsystem);
        if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &hdr64->dll_characteristics);

        if (result) result = g_binary_content_read_u64(content, pos, SRE_LITTLE, &hdr64->size_of_stack_reserve);
        if (result) result = g_binary_content_read_u64(content, pos, SRE_LITTLE, &hdr64->size_of_stack_commit);
        if (result) result = g_binary_content_read_u64(content, pos, SRE_LITTLE, &hdr64->size_of_heap_reserve);
        if (result) result = g_binary_content_read_u64(content, pos, SRE_LITTLE, &hdr64->size_of_heap_commit);

        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->loader_flags);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &hdr64->number_of_rva_and_sizes);

        directories = hdr64->data_directory;
        number_of_rva_and_sizes = &hdr64->number_of_rva_and_sizes;

    }

    if (result && *number_of_rva_and_sizes > IMAGE_NUMBEROF_DIRECTORY_ENTRIES)
    {
        log_variadic_message(LMT_BAD_BINARY,
                             _("Corrupted number of directories (%u); fixed!"),
                             *number_of_rva_and_sizes);

        *number_of_rva_and_sizes = IMAGE_NUMBEROF_DIRECTORY_ENTRIES;

    }

    for (i = 0; i < *number_of_rva_and_sizes && result; i++)
    {
        result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &directories[i].virtual_address);
        if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &directories[i].size);
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                header = structure lue à retourner. [OUT]                    *
*                next   = position en fin de lecture. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'un en-tête de programme PE.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_pe_nt_header(const GPeFormat *format, image_nt_headers *header, vmpa2t *next)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, format->dos_header.e_lfanew, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_u32(content, &pos, SRE_LITTLE, &header->signature);

    if (result) result = read_pe_file_header(format, &pos, &header->file_header);

    if (result) result = read_pe_optional_header(format, &pos, &header->optional_header);

    if (result)
        copy_vmpa(next, &pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                pos     = position de début de lecture. [OUT]                *
*                section = structure lue à retourner. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'un en-tête de section PE.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_pe_image_section_header(const GPeFormat *format, vmpa2t *pos, image_section_header *section)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    for (i = 0; i < IMAGE_SIZEOF_SHORT_NAME && result; i++)
        result = g_binary_content_read_u8(content, pos, (uint8_t *)&section->name[i]);

    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->misc.physical_address);

    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->virtual_address);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->size_of_raw_data);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->pointer_to_raw_data);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->pointer_to_relocations);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->pointer_to_line_numbers);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &section->number_of_relocations);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &section->number_of_line_numbers);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &section->characteristics);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                dir    = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un répertoire d'exportations.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_pe_image_export_directory(const GPeFormat *format, vmpa2t *pos, image_export_directory *dir)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->characteristics);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->time_date_stamp);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &dir->major_version);
    if (result) result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &dir->minor_version);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->name);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->base);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->number_of_functions);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->number_of_names);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->address_of_functions);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->address_of_names);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &dir->address_of_name_ordinals);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                desc   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un répertoire de programme PE.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_pe_image_import_descriptor(const GPeFormat *format, vmpa2t *pos, image_import_descriptor *desc)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &desc->original_first_thunk);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &desc->time_date_stamp);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &desc->forwarder_chain);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &desc->module_name);
    if (result) result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &desc->first_thunk);

    return result;

}
