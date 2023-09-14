
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.h - prototypes pour la gestion des sections d'un PE
 *
 * Copyright (C) 2010-2017 Cyrille Bagard
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


#ifndef _PLUGINS_PE_SECTION_H
#define _PLUGINS_PE_SECTION_H


#include "format.h"
#include "pe_def.h"



/* Recherche une section donnée au sein de binaire par indice. */
image_section_header *read_all_pe_sections(const GPeFormat *, vmpa2t *);



#endif  /* _PLUGINS_PE_SECTION_H */
