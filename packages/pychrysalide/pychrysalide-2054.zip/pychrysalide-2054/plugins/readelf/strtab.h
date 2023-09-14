
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strtab.h - prototypes pour la présentation des chaînes liées au format des binaires ELF
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_READELF_STRTAB_H
#define _PLUGINS_READELF_STRTAB_H


#include <format/preload.h>
#include <plugins/elf/format.h>



/* Affiche les chaînes liées aux sections ELF. */
void show_elf_section_string_table(GElfFormat *, GPreloadInfo *, GtkStatusStack *);



#endif  /* _PLUGINS_READELF_STRTAB_H */
