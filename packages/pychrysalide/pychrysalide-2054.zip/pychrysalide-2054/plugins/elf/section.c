
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.h - prototypes pour la gestion des sections d'un ELF
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


#include "section.h"


#include <malloc.h>
#include <string.h>


#include "elf-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                index   = indice de la section recherchée.                   *
*                section = ensemble d'informations à faire remonter. [OUT]    *
*                                                                             *
*  Description : Recherche une section donnée au sein de binaire par indice.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_section_by_index(const GElfFormat *format, uint16_t index, elf_shdr *section)
{
    phys_t offset;                          /* Emplacement à venir lire    */

    if (index >= ELF_HDR(format, format->header, e_shnum)) return false;

    offset = ELF_HDR(format, format->header, e_shoff)
        + ELF_HDR(format, format->header, e_shentsize) * index;

    return read_elf_section_header(format, offset, section);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                name    = nom de la section recherchée.                      *
*                section = ensemble d'informations à faire remonter. [OUT]    *
*                                                                             *
*  Description : Recherche une section donnée au sein de binaire par nom.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_section_by_name(const GElfFormat *format, const char *name, elf_shdr *section)
{
    bool result;                            /* Bilan à faire remonter      */
    elf_shdr strings;                       /* Section des descriptions    */
    uint16_t i;                             /* Boucle de parcours          */
    const char *secname;                    /* Nom d'une section analysée  */

    if (!find_elf_section_by_index(format, ELF_HDR(format, format->header, e_shstrndx), &strings))
        return false;

    result = false;

    for (i = 0; i < ELF_HDR(format, format->header, e_shnum) && !result; i++)
    {
        find_elf_section_by_index(format, i, section);

        secname = extract_name_from_elf_string_section(format, &strings,
                                                       ELF_SHDR(format, *section, sh_name));

        if (secname != NULL)
            result = (strcmp(name, secname) == 0);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                addr    = adresse de la section recherchée. (32 bits)        *
*                section = ensemble d'informations à faire remonter. [OUT]    *
*                                                                             *
*  Description : Recherche une section donnée au sein de binaire par type.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_section_by_virtual_address(const GElfFormat *format, virt_t addr, elf_shdr *section)
{
    bool result;                            /* Bilan à faire remonter      */
    uint16_t i;                             /* Boucle de parcours          */

    result = false;

    for (i = 0; i < ELF_HDR(format, format->header, e_shnum) && !result; i++)
    {
        find_elf_section_by_index(format, i, section);

        result = (addr == ELF_SHDR(format, *section, sh_addr));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = description de l'exécutable à consulter.          *
*                type     = type de la section recherchée.                    *
*                sections = tableau d'informations à faire remonter. [OUT]    *
*                count    = nombre d'éléments présents dans le tableau. [OUT] *
*                                                                             *
*  Description : Recherche une section donnée au sein de binaire par type.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_sections_by_type(const GElfFormat *format, uint32_t type, elf_shdr **sections, size_t *count)
{
    uint16_t i;                             /* Boucle de parcours          */
    elf_shdr section;                       /* Section à analyser          */

    *sections = NULL;
    *count = 0;

    for (i = 0; i < ELF_HDR(format, format->header, e_shnum); i++)
    {
        find_elf_section_by_index(format, i, &section);

        if (type == ELF_SHDR(format, section, sh_type))
        {
            *sections = (elf_shdr *)realloc(*sections, ++(*count) * sizeof(elf_shdr));
            (*sections)[*count - 1] = section;
        }

    }

    return (*count > 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                section = section à consulter.                               *
*                offset  = position de la section trouvée. [OUT]              *
*                size    = taille de la section trouvée. [OUT]                *
*                addr    = adresse virtuelle de la section trouvée. [OUT]     *
*                                                                             *
*  Description : Fournit les adresses et taille contenues dans une section.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void get_elf_section_content(const GElfFormat *format, const elf_shdr *section, phys_t *offset, phys_t *size, virt_t *addr)
{
    if (offset != NULL)
        *offset = ELF_SHDR(format, *section, sh_offset);

    if (size != NULL)
        *size = ELF_SHDR(format, *section, sh_size);

    if (addr != NULL)
    {
        *addr = ELF_SHDR(format, *section, sh_addr);

        if (*addr == 0)
        {
            if (ELF_HDR(format, format->header, e_type) == ET_REL
                || (ELF_SHDR(format, *section, sh_flags) & SHF_ALLOC) == 0)
            {
                *addr = VMPA_NO_VIRTUAL;
            }

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                section = section à consulter.                               *
*                range   = emplacement de la fonction à renseigner. [OUT]     *
*                                                                             *
*  Description : Fournit la localisation d'une section.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void get_elf_section_range(const GElfFormat *format, const elf_shdr *section, mrange_t *range)
{
    virt_t virt;                            /* Emplacement virtuel         */
    vmpa2t tmp;                             /* Enregistrement intermédiaire*/

    virt = ELF_SHDR(format, *section, sh_addr);

    if (virt == 0)
    {
        if (ELF_HDR(format, format->header, e_type) == ET_REL
            || (ELF_SHDR(format, *section, sh_flags) & SHF_ALLOC) == 0)
        {
            virt = VMPA_NO_VIRTUAL;
        }

    }

    init_vmpa(&tmp, ELF_SHDR(format, *section, sh_offset), virt);

    init_mrange(range, &tmp, ELF_SHDR(format, *section, sh_size));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                name    = nom de la section recherchée.                      *
*                offset  = position de la section trouvée. [OUT]              *
*                size    = taille de la section trouvée. [OUT]                *
*                address = adresse virtuelle de la section trouvée. [OUT]     *
*                                                                             *
*  Description : Recherche une zone donnée au sein de binaire par nom.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_section_content_by_name(const GElfFormat *format, const char *name, phys_t *offset, phys_t *size, virt_t *address)
{
    bool result;                            /* Bilan à retourner           */
    elf_shdr section;                       /* Section trouvée ou non      */

    result = find_elf_section_by_name(format, name, &section);

    if (result)
        get_elf_section_content(format, &section, offset, size, address);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                name   = nom de la section recherchée.                       *
*                range  = emplacement de la fonction à renseigner. [OUT]      *
*                                                                             *
*  Description : Recherche une zone donnée au sein de binaire par nom.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_section_range_by_name(const GElfFormat *format, const char *name, mrange_t *range)
{
    bool result;                            /* Bilan à retourner           */
    elf_shdr section;                       /* Section trouvée ou non      */

    result = find_elf_section_by_name(format, name, &section);

    if (result)
        get_elf_section_range(format, &section, range);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                section = section contenant des chaînes terminées par '\0'.  *
*                index   = indice du premier caractères à cerner.             *
*                                                                             *
*  Description : Identifie une chaîne de caractères dans une section adéquate.*
*                                                                             *
*  Retour      : Pointeur vers la chaîne recherchée ou NULL en cas d'échec.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *extract_name_from_elf_string_section(const GElfFormat *format, const elf_shdr *section, off_t index)
{
    const char *result;                     /* Nom trouvé à renvoyer       */
    phys_t last;                            /* Dernier '\0' possible       */
    phys_t phys;                            /* Point de lecture physique   */
    vmpa2t pos;                             /* Position de lecture         */
    const GBinContent *content;             /* Contenu binaire à lire      */

    last = ELF_SHDR(format, *section, sh_offset) + ELF_SHDR(format, *section, sh_size);

    phys = ELF_SHDR(format, *section, sh_offset) + index;

    if ((phys + 1) >= last)
        return NULL;

    init_vmpa(&pos, phys, VMPA_NO_VIRTUAL);

    content = G_KNOWN_FORMAT(format)->content;

    result = (const char *)g_binary_content_get_raw_access(content, &pos, 1);

    if (result == NULL)
        return NULL;

    if ((phys + strlen(result)) > last)
        return NULL;

    return result;

}
