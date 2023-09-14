
/* Chrysalide - Outil d'analyse de fichiers binaires
 * program.c - gestion des en-têtes de programme d'un ELF
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


#include "dynamic.h"


#include <assert.h>


#include "elf-int.h"
#include "program.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à consulter.           *
*                index   = indice de la section recherchée.                   *
*                dynamic = ensemble d'informations à faire remonter. [OUT]    *
*                                                                             *
*  Description : Recherche un en-tête de programme DYNAMIC au sein de binaire.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_dynamic_program_header(const GElfFormat *format, elf_phdr *dynamic)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    uint16_t max;                           /* Nombre d'en-têtes présents  */
    uint16_t i;                             /* Boucle de parcours          */

    result = false;

    max = ELF_HDR(format, format->header, e_phnum);

    for (i = 0; i < max && !result; i++)
    {
        if (!find_elf_program_by_index(format, i, dynamic))
            break;

        result = (ELF_PHDR(format, *dynamic, p_type) == PT_DYNAMIC);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                dynamic = programme de type PT_DYNAMIC.                      *
*                index   = indice de l'élément recherché.                     *
*                item    = élément retrouvé dans la section. [OUT]            *
*                                                                             *
*  Description : Retrouve un élément dans la section dynamique par son indice.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _find_elf_dynamic_item_by_index(const GElfFormat *format, const elf_phdr *dynamic, size_t index, elf_dyn *item)
{
    bool result;                            /* Bilan à retourner           */
    size_t max;                             /* Nombre d'entités présentes  */
    phys_t pos;                             /* Position de lecture         */

    max = ELF_PHDR(format, *dynamic, p_filesz) / ELF_SIZEOF_DYN(format);

    assert(index < max);

    if (index < max)
    {
        pos = ELF_PHDR(format, *dynamic, p_offset) + index * ELF_SIZEOF_DYN(format);

        result = read_elf_dynamic_entry(format, pos, item);

    }

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                index   = indice de l'élément recherché.                     *
*                item    = élément retrouvé dans la section. [OUT]            *
*                                                                             *
*  Description : Retrouve un élément dans la section dynamique par son indice.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_dynamic_item_by_index(const GElfFormat *format, size_t index, elf_dyn *item)
{
    bool result;                            /* Bilan à retourner           */
    elf_phdr dynamic;                       /* En-tête de programme DYNAMIC*/

    result = find_elf_dynamic_program_header(format, &dynamic);

    if (result)
        result = _find_elf_dynamic_item_by_index(format, &dynamic, index, item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                dynamic = programme de type PT_DYNAMIC.                      *
*                type    = sorte d'élément recherché.                         *
*                item    = élément retrouvé dans la section. [OUT]            *
*                                                                             *
*  Description : Retrouve un élément dans la section dynamique par son type.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _find_elf_dynamic_item_by_type(const GElfFormat *format, const elf_phdr *dynamic, int64_t type, elf_dyn *item)
{
    bool result;                            /* Bilan à retourner           */
    off_t max;                              /* Nombre d'entités présentes  */
    off_t i;                                /* Boucle de parcours          */
    phys_t pos;                             /* Position de lecture         */

    result = false;

    max = ELF_PHDR(format, *dynamic, p_filesz) / ELF_SIZEOF_DYN(format);

    for (i = 0; i < max && !result; i++)
    {
        pos = ELF_PHDR(format, *dynamic, p_offset) + i * ELF_SIZEOF_DYN(format);

        if (!read_elf_dynamic_entry(format, pos, item))
            break;

        result = (ELF_DYN(format, *item, d_tag) == type);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                type    = sorte d'élément recherché.                         *
*                item    = élément retrouvé dans la section. [OUT]            *
*                                                                             *
*  Description : Retrouve un élément dans la section dynamique par son type.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_elf_dynamic_item_by_type(const GElfFormat *format, int64_t type, elf_dyn *item)
{
    bool result;                            /* Bilan à retourner           */
    elf_phdr dynamic;                       /* En-tête de programme DYNAMIC*/

    result = find_elf_dynamic_program_header(format, &dynamic);

    if (result)
        result = _find_elf_dynamic_item_by_type(format, &dynamic, type, item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                count  = nombre d'éléments dans la liste constituée.         *
*                                                                             *
*  Description : Fournit la liste des objets partagés requis.                 *
*                                                                             *
*  Retour      : Liste de noms d'objets ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char **list_elf_needed_objects(const GElfFormat *format, size_t *count)
{
    const char **result;                    /* Liste à retourner           */
    elf_phdr dynamic;                       /* Programme à analyser        */
    virt_t strtab_virt;                     /* Adresse mémoire des chaînes */
    uint64_t max;                           /* Nombre d'entités présentes  */
    uint64_t i;                             /* Boucle de parcours          */
    phys_t pos;                             /* Position de lecture         */
    elf_dyn item;                           /* Informations extraites      */
    vmpa2t strtab_pos;                      /* Emplacement des chaînes     */
    GBinContent *content;                   /* Contenu global analysé      */
    vmpa2t end;                             /* Limite finale de contenu    */
    vmpa2t str_pos;                         /* Emplacement d'une chaîne    */
    phys_t diff;                            /* Données encore disponibles  */
    const bin_t *string;                    /* Nouvelle chaîne trouvée     */

    result = NULL;
    *count = 0;

    if (!find_elf_program_by_type(format, PT_DYNAMIC, &dynamic))
        goto leno_exit;

    max = ELF_PHDR(format, dynamic, p_filesz) / ELF_SIZEOF_DYN(format);

    /* Première passe : recherche des chaînes */

    strtab_virt = VMPA_NO_VIRTUAL;

    for (i = 0; i < max; i++)
    {
        pos = ELF_PHDR(format, dynamic, p_offset) + i * ELF_SIZEOF_DYN(format);

        if (!read_elf_dynamic_entry(format, pos, &item))
            break;

        if (ELF_DYN(format, item, d_tag) == DT_STRTAB)
            strtab_virt = ELF_DYN(format, item, d_un.d_val);

    }

    if (strtab_virt == VMPA_NO_VIRTUAL)
        goto leno_exit;

    if (!g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), strtab_virt, &strtab_pos))
        goto leno_exit;

    /* Seconde passe : recherche des objets requis */

    content = G_KNOWN_FORMAT(format)->content;

    g_binary_content_compute_end_pos(content, &end);

    for (i = 0; i < max; i++)
    {
        pos = ELF_PHDR(format, dynamic, p_offset) + i * ELF_SIZEOF_DYN(format);

        if (!read_elf_dynamic_entry(format, pos, &item))
            break;

        if (ELF_DYN(format, item, d_tag) == DT_NEEDED)
        {
            copy_vmpa(&str_pos, &strtab_pos);
            advance_vmpa(&str_pos, ELF_DYN(format, item, d_un.d_val));

            diff = compute_vmpa_diff(&str_pos, &end);

            string = g_binary_content_get_raw_access(content, &str_pos, diff);

            result = (const char **)realloc(result, ++(*count) * sizeof(const char *));
            result[*count - 1] = (const char *)string;

        }

    }

 leno_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à manipuler.            *
*                virt   = position en mémoire de la PLT. [OUT]                *
*                                                                             *
*  Description : Retrouve l'adresse de la PLT en se basant sur la GOT.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool resolve_plt_using_got(GElfFormat *format, virt_t *virt)
{
    bool result;                            /* Bilan à retourner           */
    elf_phdr dynamic;                       /* Programme à analyser        */
    elf_dyn pltgot;                         /* Table de type DT_PLTGOT     */
    virt_t got_virt;                        /* Adresse mémoire de la GOT   */
    vmpa2t got_addr;                        /* Localisation complète       */
    GBinContent *content;                   /* Contenu binaire à parcourir */
    uint32_t raw_32;                        /* Valeur brute de 32 bits lue */
    uint64_t raw_64;                        /* Valeur brute de 64 bits lue */

    result = false;

    if (!find_elf_program_by_type(format, PT_DYNAMIC, &dynamic))
        goto exit;

    if (!_find_elf_dynamic_item_by_type(format, &dynamic, DT_PLTGOT, &pltgot))
        goto exit;

    got_virt = ELF_DYN(format, pltgot, d_un.d_ptr);

    if (!g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), got_virt, &got_addr))
        goto exit;

    content = G_KNOWN_FORMAT(format)->content;

    /**
     * Quelques pistes pour la connaissance des premières cellules d'une GOT :
     *
     *    "Lazy procedure linkage with the PLT" (mot clef : GOT+4).
     *    http://www.iecc.com/linker/linker10.html
     *
     *    "How the ELF Ruined Christmas" (mot clef : GOT[1]).
     *     https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-di-frederico.pdf
     */

    if (format->is_32b)
    {
        advance_vmpa(&got_addr, 3 * sizeof(uint32_t));

        result = g_binary_content_read_u32(content, &got_addr, format->endian, &raw_32);

        if (result)
            *virt = raw_32;

    }

    else
    {
        advance_vmpa(&got_addr, 3 * sizeof(uint64_t));

        result = g_binary_content_read_u64(content, &got_addr, format->endian, &raw_64);

        if (result)
            *virt = raw_64;

    }

 exit:

    return result;

}
