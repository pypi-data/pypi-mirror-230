
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rich.c - calculs d'empreintes relatifs aux en-têtes PE enrichis
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


#include <format/known.h>
#include <plugins/pe/rich.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                csum   = empreinte à déterminer. [OUT]                       *
*                                                                             *
*  Description : Calcule la valeur pour empreinte d'en-tête PE enrichi.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool compute_pe_rich_header_checksum(const GPeFormat *format, uint32_t *csum)
{
    bool result;                            /* Bilan à retourner           */
    mrange_t area;                          /* Zone couverte par l'en-tête */
    GBinContent *content;                   /* Contenu à parcourir         */
    vmpa2t start;                           /* Position de départ          */
    phys_t offset;                          /* Position du début d'en-tête */
    const bin_t *data;                      /* Données brutes à analyser   */
    phys_t i;                               /* Boucle de parcours #0       */
    comp_id_t *ids;                         /* Identifiants à traiter      */
    size_t count;                           /* Quantité de ces identifiants*/
    size_t k;                               /* Boucle de parcours #1       */

    result = g_pe_format_get_rich_header_area(format, &area);

    if (!result)
        *csum = 0;

    else
    {

#define rol32(word, shift) \
        ((uint32_t)word) << (shift & 31) | ((uint32_t)word) >> (32 - (shift & 31))

        /* Première source de calculs */

        content = g_known_format_get_content(G_KNOWN_FORMAT(format));

        g_binary_content_compute_start_pos(content, &start);

        offset = get_phy_addr(get_mrange_addr(&area)) - get_phy_addr(&start);

        *csum = offset;

        data = g_binary_content_get_raw_access(content, &start, offset);
        if (data == NULL)
        {
            g_object_unref(G_OBJECT(content));
            result = false;
            goto exit;
        }

        for (i = 0; i < offset; i++)
        {
            /* Saut du champ e_lfanew, non initialisé lors de la construction */
            if (0x3c <= i && i < 0x40)
                continue;

            *csum += rol32(data[i], i);

        }

        g_object_unref(G_OBJECT(content));

        /* Seconde source de calculs */

        ids = g_pe_format_get_comp_ids(format, &count);

        for (k = 0; k < count; k++)
            *csum += rol32((ids[k].prod_id << 16) | ids[k].minor_cv, ids[k].count);

        if (ids != NULL)
            free(ids);

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                pv     = forme d'empreinte à construire.                     *
*                                                                             *
*  Description : Calcule l'empreinte des informations d'en-tête PE enrichi.   *
*                                                                             *
*  Retour      : Empreinte MD5 calculée ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *compute_pe_rich_header_hash(const GPeFormat *format, bool pv)
{
    char *result;                           /* Empreinte à retourner       */
    comp_id_t *ids;                         /* Identifiants à traiter      */
    size_t count;                           /* Quantité de ces identifiants*/
    GChecksum *checksum;                    /* Preneur d'empreinte         */
    size_t i;                               /* Boucle de parcours          */
    uint32_t value;                         /* Valeur à prendre en compte  */

    ids = g_pe_format_get_comp_ids(format, &count);

    if (ids == NULL)
        result = NULL;

    else
    {
        checksum = g_checksum_new(G_CHECKSUM_MD5);

        if (!pv)
        {
            g_checksum_update(checksum, "DanS", 4);
            g_checksum_update(checksum, "\x00\x00\x00\x00", 4);
        }

        for (i = 0; i < count; i++)
        {
            if (pv && i == 0)
                continue;

            value = (ids[i].prod_id << 16) | ids[i].minor_cv;
            g_checksum_update(checksum, (char *)&value, sizeof(value));

            if (!pv)
            {
                value = ids[i].count;
                g_checksum_update(checksum, (char *)&value, sizeof(value));
            }

        }

        result = strdup(g_checksum_get_string(checksum));

        g_checksum_free(checksum);

        free(ids);

    }

    return result;

}
