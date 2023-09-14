
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rich.h - prototypes pour les calculs d'empreintes relatifs aux en-têtes PE enrichis
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


#ifndef _PLUGINS_BHASH_RICH_H
#define _PLUGINS_BHASH_RICH_H


#include <stdbool.h>
#include <stdint.h>


#include <plugins/pe/format.h>



/* Calcule la valeur pour empreinte d'en-tête PE enrichi. */
bool compute_pe_rich_header_checksum(const GPeFormat *, uint32_t *);

/* Calcule l'empreinte des informations d'en-tête PE enrichi. */
char *compute_pe_rich_header_hash(const GPeFormat *, bool);



#endif  /* _PLUGINS_BHASH_RICH_H */
