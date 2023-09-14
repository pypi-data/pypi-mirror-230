
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.h - prototypes pour la gestion des sections d'un PE
 *
 * Copyright (C) 2010-2021 Cyrille Bagard
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


#include "pe-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                pos    = tête de lecture positionnée. [OUT]                  *
*                                                                             *
*  Description : Recherche une section donnée au sein de binaire par indice.  *
*                                                                             *
*  Retour      : Liste de sections reconstituées ou NULL en cas d'échec.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

image_section_header *read_all_pe_sections(const GPeFormat *format, vmpa2t *pos)
{
    image_section_header *result;           /* Liste à retourner           */
    uint16_t count;                         /* Quantité de sections        */
    uint16_t i;                             /* Boucle de parcours          */
    bool status;                            /* Bilan d'une lecture         */

    count = format->nt_headers.file_header.number_of_sections;

    result = malloc(count * sizeof(image_section_header));

    for (i = 0; i < count; i++)
    {
        status = read_pe_image_section_header(format, pos, &result[i]);

        if (!status)
        {
            free(result);
            result = NULL;
            break;
        }

    }

    return result;

}
