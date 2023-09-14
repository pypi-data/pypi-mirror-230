
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.h - prototypes pour l'annotation des en-têtes de section de binaires ELF
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _PLUGINS_READELF_SECTION_H
#define _PLUGINS_READELF_SECTION_H


#include <format/preload.h>
#include <plugins/elf/format.h>



/* Charge tous les symboles liés aux en-têtes de section ELF. */
bool annotate_elf_section_header_table(GElfFormat *, GPreloadInfo *, GtkStatusStack *);



#endif  /* _PLUGINS_READELF_SECTION_H */
