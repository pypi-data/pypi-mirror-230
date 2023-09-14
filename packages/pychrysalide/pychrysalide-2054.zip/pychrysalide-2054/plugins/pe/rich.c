
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rich.c - lecture des informations enrichies d'un format PE
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "rich.h"


#include <assert.h>
#include <string.h>


#include <format/known.h>


#include "pe-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                                                                             *
*  Description : Extrait si elles existant les informations enrichies du PE.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void extract_pe_rich_header(GPeFormat *format)
{
    const image_dos_header *header;         /* En-tête avec positions      */
    bin_t *dans;                            /* Motif "DanS" trouvé         */
    GBinContent *content;                   /* Contenu à parcourir         */
    vmpa2t start;                           /* Position de départ          */
    const bin_t *data;                      /* Données brutes à analyser   */
    bin_t *rich;                            /* Marqueur "Rich" trouvé      */
    uint32_t checksum;                      /* Empreinte appliquée         */
    bool status;                            /* Bilan d'une lecture         */
    bin_t words[8];                         /* Premiers mots trouvés       */

    header = g_pe_format_get_dos_header(format);

    dans = NULL;

    /* Recherche du marqueur final */

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    g_binary_content_compute_start_pos(content, &start);

    data = g_binary_content_get_raw_access(content, &start, header->e_lfanew);
    if (data == NULL) goto exit;

    rich = memmem(data, header->e_lfanew, "Rich", 4);
    if (rich == NULL) goto exit;

    /* Constitution des premiers mots */

    g_binary_content_compute_start_pos(content, &start);

    advance_vmpa(&start, rich - data);
    advance_vmpa(&start, 4);


    status = g_binary_content_read_u32(content, &start, SRE_LITTLE, &checksum);
    if (!status) goto exit;

    g_binary_content_compute_start_pos(content, &start);

    advance_vmpa(&start, rich - data);
    advance_vmpa(&start, 4);

    status = g_binary_content_read_raw(content, &start, 4, words + 4);
    assert(status);

    words[0] = 'D' ^ words[4];
    words[1] = 'a' ^ words[5];
    words[2] = 'n' ^ words[6];
    words[3] = 'S' ^ words[7];

    /* Recherche du marqueur initial et conclusion */

    dans = memmem(data, header->e_lfanew, words, 8);

    if (dans != NULL && ((rich - dans) % 8 != 0))
        dans = NULL;

 exit:

    if (dans == NULL)
    {
        init_vmpa(&start, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);
        init_mrange(&format->rich_header, &start, 0);
    }

    else
    {
        init_vmpa(&start, (bin_t *)dans - data, VMPA_NO_VIRTUAL);
        init_mrange(&format->rich_header, &start, rich + 8 - dans);
    }

    g_object_unref(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                area   = localisation à constituer. [OUT]                    *
*                                                                             *
*  Description : Décrit la zone couverte par l'en-tête enrichi du format.     *
*                                                                             *
*  Retour      : Validité de la zone définie en sortie.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_pe_format_get_rich_header_area(const GPeFormat *format, mrange_t *area)
{
    bool result;                            /* Validité à renvoyer         */

    result = (get_mrange_length(&format->rich_header) > 0);

    if (result)
        copy_mrange(area, &format->rich_header);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = format en place à consulter.                      *
*                checksum = empreinte incrustée à retrouver. [OUT]            *
*                                                                             *
*  Description : Présente l'empreinte d'un en-tête enrichi du format chargé.  *
*                                                                             *
*  Retour      : Validité de la zone définie en sortie.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_pe_format_get_rich_header_checksum(const GPeFormat *format, uint32_t *checksum)
{
    bool result;                            /* Validité à renvoyer         */
    GBinContent *content;                   /* Contenu à parcourir         */
    vmpa2t pos;                             /* Tête de lecture             */
#ifndef NDEBUG
    bool status;                            /* Bilan d'une lecture         */
#endif

    result = (get_mrange_length(&format->rich_header) > 0);

    if (result)
    {
        content = g_known_format_get_content(G_KNOWN_FORMAT(format));

        copy_vmpa(&pos, get_mrange_addr(&format->rich_header));
        advance_vmpa(&pos, sizeof(uint32_t));

#ifndef NDEBUG
        status = g_binary_content_read_u32(content, &pos, SRE_LITTLE, checksum);
        assert(status);
#else
        g_binary_content_read_u32(content, &pos, SRE_LITTLE, checksum);
#endif

        g_object_unref(G_OBJECT(content));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                count  = nombre d'éléments de la liste constituée. [OUT]     *
*                                                                             *
*  Description : Présente l'en-tête enrichi du format chargé.                 *
*                                                                             *
*  Retour      : Tableau de valeurs brutes d'information.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint64_t *g_pe_format_get_rich_header(const GPeFormat *format, size_t *count)
{
    uint64_t *result;                       /* Valeurs à retourner         */
    GBinContent *content;                   /* Contenu à parcourir         */
    vmpa2t iter;                            /* Tête de lecture             */
    size_t i;                               /* Boucle de parcours          */
#ifndef NDEBUG
    bool status;                            /* Bilan d'une lecture         */
#endif

    if (get_mrange_length(&format->rich_header) == 0)
    {
        *count = 0;
        result = NULL;
    }

    else
    {
        *count = get_mrange_length(&format->rich_header) / 8;
        result = malloc(*count * sizeof(uint64_t));

        content = g_known_format_get_content(G_KNOWN_FORMAT(format));

        copy_vmpa(&iter, get_mrange_addr(&format->rich_header));

        for (i = 0; i < *count; i++)
        {
#ifndef NDEBUG
            status = g_binary_content_read_u64(content, &iter, SRE_LITTLE, &result[i]);
            assert(status);
#else
            g_binary_content_read_u64(content, &iter, SRE_LITTLE, &result[i]);
#endif
        }

        g_object_unref(G_OBJECT(content));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                count  = nombre d'éléments de la liste constituée. [OUT]     *
*                                                                             *
*  Description : Présente les identifiants contenues dans l'en-tête enrichi.  *
*                                                                             *
*  Retour      : Tableau de valeurs raffinées d'information.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

comp_id_t *g_pe_format_get_comp_ids(const GPeFormat *format, size_t *count)
{
    comp_id_t *result;                      /* Identifiants à retourner    */
    uint64_t *values;                       /* Valeurs brutes à traiter    */
    size_t vcount;                          /* Quantité de ces valeurs     */
    uint64_t mask;                          /* Masque à appliquer          */
    size_t i;                               /* Boucle de parcours          */

    values = g_pe_format_get_rich_header(format, &vcount);

    if (vcount > 2)
    {
        mask = ((values[0] >> 32) & 0xffffffff);
        mask |= (mask << 32);

        *count = vcount - 2;
        result = malloc(*count * sizeof(comp_id_t));

        for (i = 0; i < *count; i++)
        {
            values[i + 1] ^= mask;

            result[i].minor_cv = values[i + 1] & 0xffff;
            result[i].prod_id = (values[i + 1] >> 16) & 0xffff;
            result[i].count = (values[i + 1] >> 32) & 0xffffffff;

        }

    }
    else
    {
        *count = 0;
        result = NULL;
    }

    if (values != NULL)
        free(values);

    return result;

}
