
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rich.h - prototypes pour la lecture des informations enrichies d'un format PE
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


#ifndef _PLUGINS_PE_RICH_H
#define _PLUGINS_PE_RICH_H


#include <stdint.h>


#include "format.h"



/* Extrait si elles existant les informations enrichies du PE. */
void extract_pe_rich_header(GPeFormat *);

/* Décrit la zone couverte par l'en-tête enrichi du format. */
bool g_pe_format_get_rich_header_area(const GPeFormat *, mrange_t *);

/* Présente l'empreinte d'un en-tête enrichi du format chargé. */
bool g_pe_format_get_rich_header_checksum(const GPeFormat *, uint32_t *);

/* Présente l'en-tête enrichi du format chargé. */
uint64_t *g_pe_format_get_rich_header(const GPeFormat *, size_t *);

/* Identifiants apportés par le compilateur */
typedef struct _comp_id_t
{
    uint16_t minor_cv;                      /* Version mineure du compilo  */
    uint16_t prod_id;                       /* Identifiant du type d'objet */
    uint32_t count;                         /* Nombre d'objets en cause    */

} comp_id_t;

/* Présente les identifiants contenues dans l'en-tête enrichi. */
comp_id_t *g_pe_format_get_comp_ids(const GPeFormat *, size_t *);



#endif  /* _PLUGINS_PE_RICH_H */
