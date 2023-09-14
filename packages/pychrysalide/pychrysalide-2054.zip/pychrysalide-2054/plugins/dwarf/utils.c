
/* Chrysalide - Outil d'analyse de fichiers binaires
 * utils.h - prototypes pour les fonctions d'aisance vis à vis du format DWARF
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "utils.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                pos     = position de début de lecture. [OUT]                *
*                endian  = boutisme reconnu dans le format.                   *
*                header  = en-tête à déterminer. [OUT]                        *
*                next    = position du prochain en-tête. [OUT]                *
*                                                                             *
*  Description : Procède à la lecture de l'en-tête d'un contenu binaire DWARF.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dwarf_section_header(const GBinContent *content, vmpa2t *pos, SourceEndian endian, dw_section_header *header, vmpa2t *next)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t first;                         /* Premier paquet d'octets     */
    bool status;                            /* Bilan d'opération           */

    result = false;

    status = g_binary_content_read_u32(content, pos, endian, &first);
    if (!status) goto rdsh_exit;

    if (first >= 0xfffffff0 && first != 0xffffffff)
        goto rdsh_exit;

    if (first == 0xffffffff)
    {
        result = g_binary_content_read_u64(content, pos, endian, &header->unit_length);
        header->is_32b = false;
    }
    else
    {
        result = true;
        header->unit_length = first;
        header->is_32b = true;
    }

    if (next != NULL)
    {
        copy_vmpa(next, pos);
        advance_vmpa(next, header->unit_length);
    }

    result &= g_binary_content_read_u16(content, pos, endian, &header->version);

 rdsh_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                pos     = position de début de lecture. [OUT]                *
*                endian  = boutisme reconnu dans le format.                   *
*                header  = en-tête à déterminer. [OUT]                        *
*                next    = position du prochain en-tête. [OUT]                *
*                                                                             *
*  Description : Procède à la lecture de l'en-tête d'une unité de compilation.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dwarf_compil_unit_header(GBinContent *content, vmpa2t *pos, SourceEndian endian, dw_compil_unit_header *header, vmpa2t *next)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t val32;                         /* Premier paquet d'octets     */
    bool status;                            /* Bilan d'opération           */

    result = false;

    status = read_dwarf_section_header(content, pos, endian, (dw_section_header *)header, next);
    if (!status) goto rdcuh_exit;

    if (header->is_32b)
    {
        status = g_binary_content_read_u32(content, pos, endian, &val32);
        if (!status) goto rdcuh_exit;

        header->debug_abbrev_offset = val32;

    }
    else
    {
        status = g_binary_content_read_u64(content, pos, endian, &header->debug_abbrev_offset);
        if (!status) goto rdcuh_exit;

    }

    result = g_binary_content_read_u8(content, pos, &header->address_size);

 rdcuh_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                pos     = position de début de lecture. [OUT]                *
*                decl    = structure lue à retourner. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'une déclaration d'abréviation DWARF.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dwarf_abbrev_decl(const GBinContent *content, vmpa2t *pos, dw_abbrev_decl *decl)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_uleb128(content, pos, &decl->code);

    if (result && decl->code > 0)
    {
        result = g_binary_content_read_uleb128(content, pos, &decl->tag);

        if (result)
            result = g_binary_content_read_u8(content, pos, &decl->has_children);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                pos     = position de début de lecture. [OUT]                *
*                attr    = structure lue à retourner. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'un attribut d'abréviation DWARF.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dwarf_abbrev_attr(const GBinContent *content, vmpa2t *pos, dw_abbrev_raw_attr *attr)
{
    bool result;                            /* Bilan à retourner           */

    result = g_binary_content_read_uleb128(content, pos, &attr->name);

    if (result)
        result = g_binary_content_read_uleb128(content, pos, &attr->form);

    return result;

}
