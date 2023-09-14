
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf-int.c - structures internes du format ELF
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


#include "elf-int.h"


#include <string.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                header = en-tête à déterminer. [OUT]                         *
*                is_32b = indique si le format est en 32 ou 64 bits. [OUT]    *
*                endian = boutisme reconnu dans le format. [OUT]              *
*                                                                             *
*  Description : Procède à la lecture de l'en-tête d'un contenu binaire ELF.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_header(GElfFormat *format, elf_header *header, bool *is_32b, SourceEndian *endian)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &pos, EI_NIDENT, (bin_t *)header->hdr32.e_ident);

    /* Détermination de l'espace d'adressage */
    if (result)
        switch (header->hdr32.e_ident[EI_CLASS])
        {
            case ELFCLASS32:
                *is_32b = true;
                break;
            case ELFDATA2MSB:
                *is_32b = false;
                break;
            default:
                result = false;
                break;
        }

    /* Détermination du boutisme */
    if (result)
        switch (header->hdr32.e_ident[EI_DATA])
        {
            case ELFDATA2LSB:
                *endian = SRE_LITTLE;
                break;
            case ELFDATA2MSB:
                *endian = SRE_BIG;
                break;
            default:
                result = false;
                break;
        }

    if (*is_32b)
    {
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_type);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_machine);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr32.e_version);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr32.e_entry);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr32.e_phoff);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr32.e_shoff);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr32.e_flags);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_ehsize);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_phentsize);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_phnum);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_shentsize);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_shnum);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr32.e_shstrndx);
    }
    else
    {
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_type);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_machine);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr64.e_version);
        result &= g_binary_content_read_u64(content, &pos, *endian, &header->hdr64.e_entry);
        result &= g_binary_content_read_u64(content, &pos, *endian, &header->hdr64.e_phoff);
        result &= g_binary_content_read_u64(content, &pos, *endian, &header->hdr64.e_shoff);
        result &= g_binary_content_read_u32(content, &pos, *endian, &header->hdr64.e_flags);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_ehsize);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_phentsize);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_phnum);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_shentsize);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_shnum);
        result &= g_binary_content_read_u16(content, &pos, *endian, &header->hdr64.e_shstrndx);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                phys   = position de début de lecture.                       *
*                header = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une en-tête de programme ELF.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_program_header(const GElfFormat *format, phys_t phys, elf_phdr *header)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, phys, VMPA_NO_VIRTUAL);

    if (format->is_32b)
    {
        result = g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_type);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_offset);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_vaddr);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_paddr);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_filesz);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_memsz);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_flags);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr32.p_align);
    }
    else
    {
        result = g_binary_content_read_u32(content, &pos, format->endian, &header->phdr64.p_type);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &header->phdr64.p_flags);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &header->phdr64.p_offset);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &header->phdr64.p_vaddr);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &header->phdr64.p_paddr);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &header->phdr64.p_filesz);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &header->phdr64.p_memsz);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &header->phdr64.p_align);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                phys    = position de début de lecture.                      *
*                section = section lue. [OUT]                                 *
*                                                                             *
*  Description : Procède à la lecture d'une en-tête de section ELF.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_section_header(const GElfFormat *format, phys_t phys, elf_shdr *section)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */
    elf32_shdr *shdr32;                     /* Version 32 bits             */
    elf64_shdr *shdr64;                     /* Version 32 bits             */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, phys, VMPA_NO_VIRTUAL);

    if (format->is_32b)
    {
        shdr32 = &section->shdr32;

        result = g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_name);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_type);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_flags);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_addr);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_offset);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_size);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_link);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_info);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_addralign);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr32->sh_entsize);

    }
    else
    {
        shdr64 = &section->shdr64;

        result = g_binary_content_read_u32(content, &pos, format->endian, &shdr64->sh_name);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr64->sh_type);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &shdr64->sh_flags);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &shdr64->sh_addr);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &shdr64->sh_offset);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &shdr64->sh_size);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr64->sh_link);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &shdr64->sh_info);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &shdr64->sh_addralign);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &shdr64->sh_entsize);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                phys   = position de début de lecture.                       *
*                dyn    = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une entrée de type 'DYNAMIC' ELF.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_dynamic_entry(const GElfFormat *format, phys_t phys, elf_dyn *dyn)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, phys, VMPA_NO_VIRTUAL);

    if (format->is_32b)
    {
        result = g_binary_content_read_s32(content, &pos, format->endian, &dyn->dyn32.d_tag);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &dyn->dyn32.d_un.d_val);
    }
    else
    {
        result = g_binary_content_read_s64(content, &pos, format->endian, &dyn->dyn64.d_tag);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &dyn->dyn64.d_un.d_val);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                sym    = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un symbole ELF.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_symbol(const GElfFormat *format, phys_t *phys, elf_sym *sym)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, *phys, VMPA_NO_VIRTUAL);

    if (format->is_32b)
    {
        result = g_binary_content_read_u32(content, &pos, format->endian, &sym->sym32.st_name);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &sym->sym32.st_value);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &sym->sym32.st_size);
        result &= g_binary_content_read_u8(content, &pos, &sym->sym32.st_info);
        result &= g_binary_content_read_u8(content, &pos, &sym->sym32.st_other);
        result &= g_binary_content_read_u16(content, &pos, format->endian, &sym->sym32.st_shndx);
    }
    else
    {
        result = g_binary_content_read_u32(content, &pos, format->endian, &sym->sym64.st_name);
        result &= g_binary_content_read_u8(content, &pos, &sym->sym64.st_info);
        result &= g_binary_content_read_u8(content, &pos, &sym->sym64.st_other);
        result &= g_binary_content_read_u16(content, &pos, format->endian, &sym->sym64.st_shndx);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &sym->sym64.st_value);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &sym->sym64.st_size);
    }

    if (result)
        *phys = get_phy_addr(&pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                phys   = position de début de lecture. [OUT]                 *
*                reloc  = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une relocalisation ELF.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_relocation(const GElfFormat *format, phys_t *phys, elf_rel *reloc)
{
    bool result;                            /* Bilan à retourner           */
    const GBinContent *content;             /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Position de lecture         */

    content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, *phys, VMPA_NO_VIRTUAL);

    if (format->is_32b)
    {
        result = g_binary_content_read_u32(content, &pos, format->endian, &reloc->rel32.r_offset);
        result &= g_binary_content_read_u32(content, &pos, format->endian, &reloc->rel32.r_info);
    }
    else
    {
        result = g_binary_content_read_u64(content, &pos, format->endian, &reloc->rel64.r_offset);
        result &= g_binary_content_read_u64(content, &pos, format->endian, &reloc->rel64.r_info);
    }

    if (result)
        *phys = get_phy_addr(&pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                content = contenu binaire mis à disposition ou NULL.         *
*                pos    = position de début de lecture. [OUT]                 *
*                note   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une note ELF.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_elf_note(const GElfFormat *format, GBinContent *content, phys_t *phys, elf_note *note)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Position de lecture         */

    if (content == NULL)
        content = G_KNOWN_FORMAT(format)->content;

    init_vmpa(&pos, *phys, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_u32(content, &pos, format->endian, &note->namesz);
    result &= g_binary_content_read_u32(content, &pos, format->endian, &note->descsz);
    result &= g_binary_content_read_u32(content, &pos, format->endian, &note->type);

    if (result && note->namesz > 0)
    {
        align_vmpa(&pos, 4);

        note->name = (const char *)g_binary_content_get_raw_access(content, &pos, note->namesz);

        result &= (note->name != NULL);

    }
    else note->name = NULL;

    if (result && note->descsz > 0)
    {
        align_vmpa(&pos, 4);

        note->desc = (const void *)g_binary_content_get_raw_access(content, &pos, note->descsz);

        result &= (note->desc != NULL);

    }
    else note->desc = NULL;

    return result;

}
