
/* Chrysalide - Outil d'analyse de fichiers binaires
 * form.h - prototypes pour la transmission des valeurs d'attributs
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


#include "form.h"


#include <malloc.h>


#include "format-int.h"



/* Valeurs dans DWARF */
union _dw_form_value
{
    /**
     * Version 2.
     */
    /* DW_FORM_addr */
    virt_t address;

    /* DW_FORM_data[1248] */
    uint8_t data1;
    uint16_t data2;
    uint32_t data4;
    uint64_t data8;

    /* DW_FORM_sdata */
    leb128_t sdata;

    /* DW_FORM_udata */
    uleb128_t udata;

    /* DW_FORM_block[124]? */
    struct
    {
        const bin_t *start;
        phys_t size;

    } block;

    /* DW_FORM_string */
    /* DW_FORM_strp */
    const char *string;

    /* DW_FORM_flag */
    uint8_t flag;

    /* DW_FORM_ref[1248] */
    uint8_t ref1;
    uint16_t ref2;
    uint32_t ref4;
    uint64_t ref8;

    /* DW_FORM_ref_udata */
    uleb128_t ref_udata;


    /**
     * Version 4.
     */

    /* DW_FORM_sec_offset */
    uint64_t sec_offset;

    /* DW_FORM_exprloc */
    struct
    {
        const bin_t *start;
        phys_t size;

    } expr;

    /* DW_FORM_flag_present */
    bool has_flag;

    /* DW_FORM_ref_sig8 */
    uint64_t signature;

};


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = contenu binaire de débogage à parcourir.           *
*                content = contenu encadré à parcourir.                       *
*                pos     = tête de lecture au sein des données. [OUT]         *
*                cu      = unité de compilation parente.                      *
*                form    = nature de la valeur à lire.                        *
*                output  = valeur au format donné lue. [OUT]                  *
*                                                                             *
*  Description : Lit la valeur correspondant à un type donné.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dwarf_form_value(const GDwarfFormat *format, GBinContent *content, vmpa2t *pos, const dw_compil_unit_header *cu, DwarfForm form, dw_form_value **output)
{
    bool result;                            /* Bilan de lecture à renvoyer */
    dw_form_value *value;                   /* Valeur constituée           */
    SourceEndian endian;                    /* Boutisme des enregistrements*/


    const bin_t *tmp;                       /* Données quelconques         */
    uint8_t tmp8;                           /* Données sur 8 bits          */
    uint16_t tmp16;                         /* Données sur 16 bits         */
    uint32_t tmp32;                         /* Données sur 32 bits         */
    uint64_t tmp64;                         /* Données sur 64 bits         */
    uleb128_t tmpuleb;                      /* Données sur xxx bits        */
    phys_t offset;                          /* Décalage à appliquer        */
    GExeFormat *exe;                        /* Format d'exécutable rattaché*/
    mrange_t range;                         /* Couverture d'une section    */
    vmpa2t iter;                            /* Point de lecture parallèle  */


    value = (dw_form_value *)malloc(sizeof(dw_form_value));

    endian = g_binary_format_get_endianness(G_BIN_FORMAT(format));

    switch (form)
    {




        /* Version 2 */


        case DW_FORM_addr:

            switch (cu->address_size)
            {
                case 2:
                    result = g_binary_content_read_u16(content, pos, endian, &tmp16);
                    if (result) value->address = tmp16;
                    break;
                case 4:
                    result = g_binary_content_read_u32(content, pos, endian, &tmp32);
                    if (result) value->address = tmp32;
                    break;
                case 8:
                    result = g_binary_content_read_u64(content, pos, endian, &tmp64);
                    if (result) value->address = tmp64;
                    break;
                default:
                    result = false;
                    break;
            }
            break;

        case DW_FORM_block2:
            result = g_binary_content_read_u16(content, pos, endian, &tmp16);
            if (result)
            {
                value->block.size = tmp16;
                goto block_finish;
            }
            break;

        case DW_FORM_block4:
            result = g_binary_content_read_u32(content, pos, endian, &tmp32);
            if (result)
            {
                value->block.size = tmp32;
                goto block_finish;
            }
            break;

        case DW_FORM_data2:
            result = g_binary_content_read_u16(content, pos, endian, &value->data2);
            break;

        case DW_FORM_data4:
            result = g_binary_content_read_u32(content, pos, endian, &value->data4);
            break;

        case DW_FORM_data8:
            result = g_binary_content_read_u64(content, pos, endian, &value->data8);
            break;

        case DW_FORM_string:

            tmp = g_binary_content_get_raw_access(content, pos, 1);
            result = (tmp != NULL);

            if (result)
            {
                value->string = (const char *)tmp;

                while (result && *tmp != '\0')
                {
                    tmp = g_binary_content_get_raw_access(content, pos, 1);
                    result = (tmp != NULL);
                }

            }

            break;

        case DW_FORM_block:

            tmpuleb = 0;    /* Pour GCC */

            result = g_binary_content_read_uleb128(content, pos, &tmpuleb);
            if (!result) break;

            value->block.size = tmpuleb;

 block_finish:

            value->block.start = g_binary_content_get_raw_access(content, pos, value->block.size);

            result = (value->block.start != NULL);
            break;

        case DW_FORM_block1:
            result = g_binary_content_read_u8(content, pos, &tmp8);
            if (result)
            {
                value->block.size = tmp8;
                goto block_finish;
            }
            break;

        case DW_FORM_data1:
            result = g_binary_content_read_u8(content, pos, &value->data1);
            break;

        case DW_FORM_flag:
            result = g_binary_content_read_u8(content, pos, &value->flag);
            break;

        case DW_FORM_sdata:
            result = g_binary_content_read_leb128(content, pos, &value->sdata);
            break;

        case DW_FORM_strp:

            /* Définition des positions */

            if (cu->is_32b)
            {
                    result = g_binary_content_read_u32(content, pos, endian, &tmp32);
                    offset = tmp32;
            }
            else
            {
                result = g_binary_content_read_u64(content, pos, endian, &tmp64);
                offset = tmp64;
            }

            /* Lecture dans la section adaptée */

            if (result)
            {
                exe = G_DBG_FORMAT(format)->executable;
                result = g_exe_format_get_section_range_by_name(exe, ".debug_str", &range);
            }

            if (result)
            {
                copy_vmpa(&iter, get_mrange_addr(&range));

                result = g_binary_content_seek(content, &iter, offset);

                if (!result)
                    break;

                tmp = g_binary_content_get_raw_access(content, &iter, 1);
                result = (tmp != NULL);

                if (result)
                {
                    value->string = (const char *)tmp;

                    while (result && *tmp != '\0')
                    {
                        tmp = g_binary_content_get_raw_access(content, &iter, 1);
                        result = (tmp != NULL);
                    }

                }

            }

            break;

        case DW_FORM_udata:
            result = g_binary_content_read_uleb128(content, pos, &value->udata);
            break;











        case DW_FORM_ref1:
            result = g_binary_content_read_u8(content, pos, &value->ref1);
            break;

        case DW_FORM_ref2:
            result = g_binary_content_read_u16(content, pos, endian, &value->ref2);
            break;

        case DW_FORM_ref4:
            result = g_binary_content_read_u32(content, pos, endian, &value->ref4);
            break;

        case DW_FORM_ref8:
            result = g_binary_content_read_u64(content, pos, endian, &value->ref8);
            break;

        case DW_FORM_ref_udata:
            result = g_binary_content_read_uleb128(content, pos, &value->ref_udata);
            break;
















        /* Version 4 */

        case DW_FORM_sec_offset:

            if (cu->is_32b)
            {
                    result = g_binary_content_read_u32(content, pos, endian, &tmp32);
                    tmp64 = tmp32;
            }
            else
                result = g_binary_content_read_u64(content, pos, endian, &tmp64);

            value->sec_offset = tmp64;
            break;

        case DW_FORM_exprloc:

            //tmpuleb = 0;    /* Pour GCC */

            result = g_binary_content_read_uleb128(content, pos, &tmpuleb);
            if (!result) break;

            value->expr.size = tmpuleb;

            value->expr.start = g_binary_content_get_raw_access(content, pos, value->expr.size);
            result = (value->expr.start != NULL);

            break;

        case DW_FORM_flag_present:
            result = true;
            value->has_flag = true;
            break;

        case DW_FORM_ref_sig8:
            result = g_binary_content_read_u64(content, pos, endian, &value->signature);
            break;

        default:
            result = false;
            break;

    }

    if (result)
        *output = value;
    else
        free_dwarf_form_value(value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur à librérer de la mémoire.                     *
*                                                                             *
*  Description : Supprime de la mémoire une valeur correspondant à un type.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void free_dwarf_form_value(dw_form_value *value)
{
    free(value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur au format Dwarf à consulter.                  *
*                form   = nature de la valeur à lire.                         *
*                addr   = valeur utilisable en interne récupérée. [OUT]       *
*                                                                             *
*  Description : Transcrit une valeur Dwarf brute en adresse virtuelle.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool translate_form_into_address(const dw_form_value *value, DwarfForm form, virt_t *addr)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    switch (form)
    {
        case DW_FORM_addr:
            *addr = value->address;
            break;

        case DW_FORM_data1:
            *addr = value->data1;
            break;

        case DW_FORM_data2:
            *addr = value->data2;
            break;

        case DW_FORM_data4:
            *addr = value->data4;
            break;

        case DW_FORM_data8:
            *addr = value->data8;
            break;

        default:
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur au format Dwarf à consulter.                  *
*                form   = nature de la valeur à lire.                         *
*                                                                             *
*  Description : Transcrit une valeur Dwarf brute en chaîne de caractères.    *
*                                                                             *
*  Retour      : Bilan de l'opération : chaîne de caractères ou NULL si échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *translate_form_into_string(const dw_form_value *value, DwarfForm form)
{
    const char *result;                     /* Valeur et bilan à retourner */

    switch (form)
    {
        case DW_FORM_string:
        case DW_FORM_strp:
            result = value->string;
            break;

        default:
            result = NULL;
            break;

    }

    return result;

}
