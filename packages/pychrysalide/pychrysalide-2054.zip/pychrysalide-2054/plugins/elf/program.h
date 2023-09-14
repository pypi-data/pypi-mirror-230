
/* Chrysalide - Outil d'analyse de fichiers binaires
 * program.h - prototypes pour la gestion des en-têtes de programme d'un ELF
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


#ifndef _PLUGINS_ELF_PROGRAM_H
#define _PLUGINS_ELF_PROGRAM_H


#include "elf_def.h"
#include "format.h"



/* Fournit la description humaine d'un type de segment ELF. */
const char *get_elf_program_type_desc(const GElfFormat *, uint32_t);

/* Recherche un programme donné au sein de binaire par indice. */
bool find_elf_program_by_index(const GElfFormat *, uint16_t, elf_phdr *);

/* Recherche un programme donné au sein de binaire par type. */
bool find_elf_program_by_type(const GElfFormat *, uint32_t, elf_phdr *);



#endif  /* _PLUGINS_ELF_PROGRAM_H */
