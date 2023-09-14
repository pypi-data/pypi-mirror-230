
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dynamic.h - prototypes pour la manipulation de l'en-ête de programme 'DYNAMIC'
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


#ifndef _PLUGINS_ELF_DYNAMIC_H
#define _PLUGINS_ELF_DYNAMIC_H


#include "elf_def.h"
#include "format.h"



/* Recherche un en-tête de programme DYNAMIC au sein de binaire. */
bool find_elf_dynamic_program_header(const GElfFormat *, elf_phdr *);

/* Retrouve un élément dans la section dynamique par son indice. */
bool _find_elf_dynamic_item_by_index(const GElfFormat *, const elf_phdr *, size_t, elf_dyn *);

/* Retrouve un élément dans la section dynamique par son indice. */
bool find_elf_dynamic_item_by_index(const GElfFormat *, size_t, elf_dyn *);

/* Retrouve un élément dans la section dynamique par son type. */
bool _find_elf_dynamic_item_by_type(const GElfFormat *, const elf_phdr *, int64_t, elf_dyn *);

/* Retrouve un élément dans la section dynamique par son type. */
bool find_elf_dynamic_item_by_type(const GElfFormat *, int64_t, elf_dyn *);

/* Fournit la liste des objets partagés requis. */
const char **list_elf_needed_objects(const GElfFormat *, size_t *);

/* Retrouve l'adresse de la PLT en se basant sur la GOT. */
bool resolve_plt_using_got(GElfFormat *, virt_t *);



#endif  /* _PLUGINS_ELF_DYNAMIC_H */
