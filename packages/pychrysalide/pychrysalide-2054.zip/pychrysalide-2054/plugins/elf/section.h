
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.h - prototypes pour la gestion des sections d'un ELF
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


#ifndef _PLUGINS_ELF_SECTION_H
#define _PLUGINS_ELF_SECTION_H


#include "elf_def.h"
#include "format.h"



/* Recherche une section donnée au sein de binaire par indice. */
bool find_elf_section_by_index(const GElfFormat *, uint16_t, elf_shdr *);

/* Recherche une section donnée au sein de binaire par nom. */
bool find_elf_section_by_name(const GElfFormat *, const char *, elf_shdr *);

/* Recherche une section donnée au sein de binaire par type. */
bool find_elf_section_by_virtual_address(const GElfFormat *, virt_t, elf_shdr *);

/* Recherche une section donnée au sein de binaire par type. */
bool find_elf_sections_by_type(const GElfFormat *, uint32_t, elf_shdr **, size_t *);

/* Fournit les adresses et taille contenues dans une section. */
void get_elf_section_content(const GElfFormat *, const elf_shdr *, phys_t *, phys_t *, virt_t *);

/* Fournit la localisation d'une section. */
void get_elf_section_range(const GElfFormat *, const elf_shdr *, mrange_t *);

/* Recherche une zone donnée au sein de binaire par nom. */
bool find_elf_section_content_by_name(const GElfFormat *, const char *, phys_t *, phys_t *, virt_t *);

/* Recherche une zone donnée au sein de binaire par nom. */
bool find_elf_section_range_by_name(const GElfFormat *, const char *, mrange_t *);

/* Identifie une chaîne de caractères dans une section adéquate. */
const char *extract_name_from_elf_string_section(const GElfFormat *, const elf_shdr *, off_t);



#endif  /* _PLUGINS_ELF_SECTION_H */
