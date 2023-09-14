
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dex-int.c - structures internes du format DEX
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#include "dex-int.h"


#include <assert.h>
#include <malloc.h>


#include <i18n.h>


#include <common/endianness.h>
#include <common/utf8.h>
#include <plugins/dalvik/pseudo/identifiers.h>



/* ---------------------------------------------------------------------------------- */
/*                            DESCRIPTION DU FORMAT DALVIK                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                header = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une en-tête de programme DEX.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_header(const GDexFormat *format, vmpa2t *pos, dex_header *header)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    size_t i;                               /* Boucle de parcours          */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    for (i = 0; i < DEX_FILE_MAGIC_LEN && result; i++)
        result = g_binary_content_read_u8(content, pos, &header->magic[i]);

    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->checksum);

    for (i = 0; i < 20 && result; i++)
        result = g_binary_content_read_u8(content, pos, &header->signature[i]);

    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->file_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->header_size);

    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->endian_tag);

    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->link_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->link_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->map_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->string_ids_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->string_ids_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->type_ids_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->type_ids_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->proto_ids_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->proto_ids_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->field_ids_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->field_ids_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->method_ids_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->method_ids_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->class_defs_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->class_defs_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->data_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &header->data_off);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          ELEMENTS DE TABLE DES CONSTANTES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                str_id = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un identifiant de chaîne DEX.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_string_id_item(const GDexFormat *format, vmpa2t *pos, string_id_item *str_id)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &str_id->string_data_off);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = informations chargées à consulter.                *
*                pos      = position de début de lecture. [OUT]               *
*                inter    = position intermédiaire à conserver. [OUT]         *
*                str_data = structure lue à retourner. [OUT]                  *
*                                                                             *
*  Description : Procède à la lecture de proriétés de chaîne DEX.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_string_data_item(const GDexFormat *format, vmpa2t *pos, vmpa2t *inter, string_data_item *str_data)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    size_t consumed;                        /* Taille effective des données*/
    phys_t fullsize;                        /* Taille complète du contenu  */
    vmpa2t old;                             /* Sauvegarde de position      */
    uleb128_t i;                            /* Boucle de parcours          */
    phys_t maxsize;                         /* Taille maximale d'une unité */
    const bin_t *tmp;                       /* Zone de parcours temporaire */
    size_t used;                            /* Quantié d'octets consommés  */
    unichar_t ch;                           /* Unité de code MUTF-8        */

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_uleb128(content, pos, &str_data->utf16_size);

    if (result)
    {
        if (inter != NULL)
            copy_vmpa(inter, pos);

        consumed = 0;

        fullsize = g_binary_content_compute_size(content);

        copy_vmpa(&old, pos);

        for (i = 0; i < (str_data->utf16_size + 1) && result; i++)
        {
            if (i > 0)
            {
                copy_vmpa(pos, &old);
                advance_vmpa(pos, consumed);
            }

            /**
             * Théoriquement, les 4 octets maximaux pour l'encodage ne sont pas
             * forcément tous disponibles...
             *
             * Il est alors possible d'obtenir une erreur pour un caractère
             * légitime d'un octet.
             *
             * On borne donc la taille de la prochaine unité MUTF-8.
             */

            maxsize = fullsize - get_phy_addr(pos);

            if (maxsize > 4)
                maxsize = 4;

            tmp = g_binary_content_get_raw_access(content, pos, maxsize);

            ch = decode_mutf8_char(tmp, maxsize, &used);

            if (IS_UTF8_ERROR(ch))
                result = false;

            else
                consumed += used;

            if (i == str_data->utf16_size)
                result = (ch == 0x0);

        }

        copy_vmpa(pos, &old);

        if (result)
        {
            str_data->data = g_binary_content_get_raw_access(content, pos, consumed);
            result = (str_data->data != NULL);
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                item   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un identifiant de type DEX.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_type_id_item(const GDexFormat *format, vmpa2t *pos, type_id_item *item)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &item->descriptor_idx);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = informations chargées à consulter.                *
*                pos      = position de début de lecture. [OUT]               *
*                proto_id = structure lue à retourner. [OUT]                  *
*                                                                             *
*  Description : Procède à la lecture d'une description de prototype.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_proto_id_item(const GDexFormat *format, vmpa2t *pos, proto_id_item *proto_id)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &proto_id->shorty_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &proto_id->return_type_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &proto_id->parameters_off);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = informations chargées à consulter.                *
*                pos      = position de début de lecture. [OUT]               *
*                field_id = structure lue à retourner. [OUT]                  *
*                                                                             *
*  Description : Procède à la lecture d'une description de champ.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_field_id_item(const GDexFormat *format, vmpa2t *pos, field_id_item *field_id)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &field_id->class_idx);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &field_id->type_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &field_id->name_idx);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                pos     = position de début de lecture. [OUT]                *
*                meth_id = structure lue à retourner. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'une description de méthode.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_method_id_item(const GDexFormat *format, vmpa2t *pos, method_id_item *meth_id)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &meth_id->class_idx);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &meth_id->proto_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &meth_id->name_idx);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format    = informations chargées à consulter.               *
*                pos       = position de début de lecture. [OUT]              *
*                class_def = structure lue à retourner. [OUT]                 *
*                                                                             *
*  Description : Procède à la lecture des propriétés d'une classe DEX.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_class_def_item(const GDexFormat *format, vmpa2t *pos, class_def_item *class_def)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->class_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->access_flags);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->superclass_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->interfaces_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->source_file_idx);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->annotations_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->class_data_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &class_def->static_values_off);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             DESCRIPTION DE CLASSES DEX                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                field  = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un champ quelconque DEX.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_encoded_field(const GDexFormat *format, vmpa2t *pos, encoded_field *field)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_uleb128(content, pos, &field->field_idx_diff);
    result &= g_binary_content_read_uleb128(content, pos, &field->access_flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                method = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une méthode quelconque DEX.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_encoded_method(const GDexFormat *format, vmpa2t *pos, encoded_method *method)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    copy_vmpa(&method->origin, pos);

    result &= g_binary_content_read_uleb128(content, pos, &method->method_idx_diff);
    result &= g_binary_content_read_uleb128(content, pos, &method->access_flags);
    result &= g_binary_content_read_uleb128(content, pos, &method->code_off);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                item   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un type DEX.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_type_item(const GDexFormat *format, vmpa2t *pos, type_item *item)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    content = G_KNOWN_FORMAT(format)->content;

    result = g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->type_idx);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                list   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une liste de types DEX.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_type_list(const GDexFormat *format, vmpa2t *pos, type_list *list)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &list->size);

    list->list = (const type_item *)g_binary_content_get_raw_access(content, pos, list->size * sizeof(type_item));
    result &= (list->list != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                item   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un contenu de classe DEX.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_class_data_item(const GDexFormat *format, vmpa2t *pos, class_data_item *item)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    uleb128_t i;                            /* Boucle de parcours          */

    result = true;

    item->static_fields = NULL;
    item->instance_fields = NULL;
    item->direct_methods = NULL;
    item->virtual_methods = NULL;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_uleb128(content, pos, &item->static_fields_size);
    result &= g_binary_content_read_uleb128(content, pos, &item->instance_fields_size);
    result &= g_binary_content_read_uleb128(content, pos, &item->direct_methods_size);
    result &= g_binary_content_read_uleb128(content, pos, &item->virtual_methods_size);

    if (result && item->static_fields_size > 0)
    {
        item->static_fields = (encoded_field *)calloc(item->static_fields_size, sizeof(encoded_field));
        if (item->static_fields == NULL) item->static_fields_size = 0;

        for (i = 0; i < item->static_fields_size && result; i++)
            result = read_dex_encoded_field(format, pos, &item->static_fields[i]);

    }

    if (result && item->instance_fields_size > 0)
    {
        item->instance_fields = (encoded_field *)calloc(item->instance_fields_size, sizeof(encoded_field));
        if (item->instance_fields == NULL) item->instance_fields_size = 0;

        for (i = 0; i < item->instance_fields_size && result; i++)
            result = read_dex_encoded_field(format, pos, &item->instance_fields[i]);

    }

    if (result && item->direct_methods_size > 0)
    {
        item->direct_methods = (encoded_method *)calloc(item->direct_methods_size, sizeof(encoded_method));
        if (item->direct_methods == NULL) item->direct_methods_size = 0;

        for (i = 0; i < item->direct_methods_size && result; i++)
            result = read_dex_encoded_method(format, pos, &item->direct_methods[i]);

    }

    if (result && item->virtual_methods_size > 0)
    {
        item->virtual_methods = (encoded_method *)calloc(item->virtual_methods_size, sizeof(encoded_method));
        if (item->virtual_methods == NULL) item->virtual_methods_size = 0;

        for (i = 0; i < item->virtual_methods_size && result; i++)
            result = read_dex_encoded_method(format, pos, &item->virtual_methods[i]);

    }

    if (!result)
        reset_dex_class_data_item(item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = structure à nettoyer.                                 *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_class_data_item(class_data_item *item)
{
    if (item->static_fields != NULL)
        free(item->static_fields);

    if (item->instance_fields != NULL)
        free(item->instance_fields);

    if (item->direct_methods != NULL)
        free(item->direct_methods);

    if (item->virtual_methods != NULL)
        free(item->virtual_methods);

}



/* ---------------------------------------------------------------------------------- */
/*                             PORTION DE CODE EXECUTABLE                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                pair   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une association exception <-> code.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_encoded_type_addr_pair(const GDexFormat *format, vmpa2t *pos, encoded_type_addr_pair *pair)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_uleb128(content, pos, &pair->type_idx);
    result &= g_binary_content_read_uleb128(content, pos, &pair->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                pos     = position de début de lecture. [OUT]                *
*                handler = structure lue à retourner. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'une association exception <-> code.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_encoded_catch_handler(const GDexFormat *format, vmpa2t *pos, encoded_catch_handler *handler)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    leb128_t count;                         /* Nombre de gestionnaires     */
    leb128_t i;                             /* Boucle de parcours          */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    handler->offset = get_phy_addr(pos);

    result &= g_binary_content_read_leb128(content, pos, &handler->size);

    count = leb128_abs(handler->size);

    if (count > 0 && result)
    {
        handler->handlers = (encoded_type_addr_pair *)calloc(count, sizeof(encoded_type_addr_pair));

        for (i = 0; i < count && result; i++)
            result &= read_dex_encoded_type_addr_pair(format, pos, &handler->handlers[i]);

    }
    else handler->handlers = NULL;

    if (handler->size <= 0)
        result &= g_binary_content_read_uleb128(content, pos, &handler->catch_all_addr);

    else
        handler->catch_all_addr = ULEB128_MAX;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = structure à nettoyer.                              *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_encoded_catch_handler(encoded_catch_handler *handler)
{
    if (handler->handlers != NULL)
        free(handler->handlers);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                list   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une association exception <-> code.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_encoded_catch_handler_list(const GDexFormat *format, vmpa2t *pos, encoded_catch_handler_list *list)
{
    bool result;                            /* Bilan à retourner           */
    off_t saved_off;                        /* Sauvegarde de position      */
    GBinContent *content;                   /* Contenu binaire à lire      */
    uleb128_t i;                            /* Boucle de parcours          */

    result = true;

    saved_off = get_phy_addr(pos);

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_uleb128(content, pos, &list->size);

    if (list->size > 0 && result)
    {
        list->list = (encoded_catch_handler *)calloc(list->size, sizeof(encoded_catch_handler));

        for (i = 0; i < list->size && result; i++)
        {
            result &= read_dex_encoded_catch_handler(format, pos, &list->list[i]);
            if (result) list->list[i].offset -= saved_off;
        }

    }
    else list->list = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = structure à nettoyer.                                 *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_encoded_catch_handler_list(encoded_catch_handler_list *list)
{
    uleb128_t i;                            /* Boucle de parcours          */

    if (list->list != NULL)
    {
        for (i = 0; i < list->size; i++)
            reset_dex_encoded_catch_handler(&list->list[i]);

        free(list->list);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                item   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une association exception <-> code.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_try_item(const GDexFormat *format, vmpa2t *pos, try_item *item)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &item->start_addr);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->insn_count);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->handler_off);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                item   = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'une portion de code DEX.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_code_item(const GDexFormat *format, vmpa2t *pos, code_item *item)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    vmpa2t origin;                          /* Mémorisation d'une position */
    uint16_t padding;                       /* Eventuel alignement         */
    uint16_t i;                             /* Boucle de parcours          */

    /* Respect de l'alignement sur 4 octets */
    if (get_phy_addr(pos) % 4 != 0) return false;

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->registers_size);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->ins_size);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->outs_size);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &item->tries_size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &item->debug_info_off);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &item->insns_size);

    item->insns = (uint16_t *)g_binary_content_get_raw_access(content, pos, item->insns_size * sizeof(uint16_t));
    if (item->insns == NULL) goto rdci_bad_insns;

    /* Padding ? */
    if (item->tries_size > 0 && item->insns_size % 2 == 1)
    {
        copy_vmpa(&origin, pos);

        result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &padding);

        if (padding != 0)
            g_binary_format_add_error(G_BIN_FORMAT(format), BFE_SPECIFICATION, &origin,
                                      _("Expected a null value as padding."));

    }

    if (item->tries_size > 0 && result)
    {
        assert(get_phy_addr(pos) % 4 == 0);

        item->tries = (try_item *)calloc(item->tries_size, sizeof(try_item));
        if (item->tries == NULL) goto rdci_bad_tries;

        for (i = 0; i < item->tries_size && result; i++)
            result &= read_dex_try_item(format, pos, &item->tries[i]);

        if (result)
        {
            item->handlers = (encoded_catch_handler_list *)calloc(1, sizeof(encoded_catch_handler_list));
            result &= read_dex_encoded_catch_handler_list(format, pos, item->handlers);
        }

        else
            item->handlers = NULL;

    }

    else
    {
        item->tries = NULL;
        item->handlers = NULL;
    }

    return result;

 rdci_bad_insns:

    item->tries = NULL;

 rdci_bad_tries:

    item->handlers = NULL;

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = structure à nettoyer.                                 *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_code_item(code_item *item)
{
    if (item->tries != NULL)
        free(item->tries);

    if (item->handlers != NULL)
    {
        reset_dex_encoded_catch_handler_list(item->handlers);
        free(item->handlers);
    }

}



/* ---------------------------------------------------------------------------------- */
/*                                 AIGUILLAGES DIVERS                                 */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                packed = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un contenu d'aiguillage compact.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_packed_switch(const GDexFormat *format, vmpa2t *pos, packed_switch *packed)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    uint16_t i;                             /* Boucle de parcours          */

    result = true;

    packed->targets = NULL;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &packed->ident);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &packed->size);
    result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &packed->first_key);

    if (result && packed->size > 0)
    {
        packed->targets = (uint32_t *)calloc(packed->size, sizeof(uint32_t));

        for (i = 0; i < packed->size && result; i++)
            result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &packed->targets[i]);

    }

    if (!result)
        reset_dex_packed_switch(packed);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : packed = structure à nettoyer.                               *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_packed_switch(packed_switch *packed)
{
    if (packed->targets != NULL)
        free(packed->targets);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                pos    = position de début de lecture. [OUT]                 *
*                sparse = structure lue à retourner. [OUT]                    *
*                                                                             *
*  Description : Procède à la lecture d'un contenu d'aiguillage dispersé.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_sparse_switch(const GDexFormat *format, vmpa2t *pos, sparse_switch *sparse)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    uint16_t i;                             /* Boucle de parcours          */

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    sparse->keys = NULL;
    sparse->targets = NULL;

    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &sparse->ident);
    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &sparse->size);

    if (result && sparse->size > 0)
    {
        sparse->keys = (uint32_t *)calloc(sparse->size, sizeof(uint32_t));
        sparse->targets = (uint32_t *)calloc(sparse->size, sizeof(uint32_t));

        for (i = 0; i < sparse->size && result; i++)
            result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &sparse->keys[i]);

        for (i = 0; i < sparse->size && result; i++)
            result &= g_binary_content_read_u32(content, pos, SRE_LITTLE, &sparse->targets[i]);

    }

    if (!result)
        reset_dex_sparse_switch(sparse);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sparse = structure à nettoyer.                               *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_sparse_switch(sparse_switch *sparse)
{
    if (sparse->keys != NULL)
        free(sparse->keys);

    if (sparse->targets != NULL)
        free(sparse->targets);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                pos     = position de début de lecture. [OUT]                *
*                dsxitch = structure lue à retourner. [OUT]                   *
*                                                                             *
*  Description : Procède à la lecture d'un contenu d'aiguillage Dex interne.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_dex_switch(const GDexFormat *format, vmpa2t *pos, dex_switch *dswitch)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à lire      */
    uint16_t ident;                         /* Pseudo-code d'identification*/

    result = true;

    content = G_KNOWN_FORMAT(format)->content;

    result &= g_binary_content_read_u16(content, pos, SRE_LITTLE, &ident);

    /**
     * La tête de lecture n'est pas mise à jour volontairement !
     */

    if (result)
    {
        if (ident == DPO_PACKED_SWITCH)
            result = read_dex_packed_switch(format, pos, (packed_switch *)dswitch);

        else if (ident == DPO_SPARSE_SWITCH)
            result = read_dex_sparse_switch(format, pos, (sparse_switch *)dswitch);

        else
            result = false;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dswitch = structure à nettoyer.                              *
*                                                                             *
*  Description : Supprime tous les éléments chargés en mémoire à la lecture.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_dex_switch(dex_switch *dswitch)
{
    if (dswitch->packed.ident == DPO_PACKED_SWITCH)
        reset_dex_packed_switch((packed_switch *)dswitch);
    else
        reset_dex_sparse_switch((sparse_switch *)dswitch);

}
