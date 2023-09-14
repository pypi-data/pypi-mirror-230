
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf-int.h - prototypes pour les structures internes du format ELF
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


#ifndef _PLUGINS_ELF_ELF_INT_H
#define _PLUGINS_ELF_ELF_INT_H


#include <common/endianness.h>
#include <format/executable-int.h>


#include "elf_def.h"
#include "format.h"



/* Fournit la description humaine d'un type de segment ELF. */
typedef const char * (* get_elf_prgm_type_desc_cb) (uint32_t);

/* Fournit une adresse virtuelle prête à emploi. */
typedef virt_t (* fix_elf_virt_addr_cb) (virt_t);

/* Détermine l'emplacement de la première entrée dans la PLT. */
typedef bool (* find_first_plt_entry_cb) (GElfFormat *, vmpa2t *);

/* Retrouve le décalage appliqué lors d'une résolution. */
typedef bool (* get_elf_linkage_offset_cb) (GElfFormat *, vmpa2t *, uint64_t *);



/* Particularités propre aux architectures */
typedef struct _elf_arch_ops
{
    get_elf_prgm_type_desc_cb get_type_desc;/* Description de type         */
    fix_elf_virt_addr_cb fix_virt;          /* Retire toute forme d'infos  */
    find_first_plt_entry_cb find_first_plt; /* Recherche d'entrée de PLT   */
    get_elf_linkage_offset_cb get_linkage_offset; /* Décalage de relocation*/

} elf_arch_ops;


/* Format d'exécutable générique (instance) */
struct _GElfFormat
{
    GExeFormat parent;                      /* A laisser en premier        */

    elf_header header;                      /* En-tête du format           */
    bool is_32b;                            /* Format du binaire           */
    SourceEndian endian;                    /* Boutisme du format          */

    elf_arch_ops ops;                       /* Opérations spécifiques      */

};

/* Format d'exécutable générique (classe) */
struct _GElfFormatClass
{
    GExeFormatClass parent;                 /* A laisser en premier        */

};



/* Procède à la lecture de l'en-tête d'un contenu binaire ELF. */
bool read_elf_header(GElfFormat *, elf_header *, bool *, SourceEndian *);

/* Procède à la lecture d'une en-tête de programme ELF. */
bool read_elf_program_header(const GElfFormat *, phys_t, elf_phdr *);

/* Procède à la lecture d'une en-tête de section ELF. */
bool read_elf_section_header(const GElfFormat *, phys_t, elf_shdr *);

/* Procède à la lecture d'une entrée de type 'DYNAMIC' ELF. */
bool read_elf_dynamic_entry(const GElfFormat *, phys_t, elf_dyn *);

/* Procède à la lecture d'un symbole ELF. */
bool read_elf_symbol(const GElfFormat *, phys_t *, elf_sym *);

/* Procède à la lecture d'une relocalisation ELF. */
bool read_elf_relocation(const GElfFormat *, phys_t *, elf_rel *);

/* Procède à la lecture d'une note ELF. */
bool read_elf_note(const GElfFormat *, GBinContent *, phys_t *, elf_note *);



#endif  /* _PLUGINS_ELF_ELF_INT_H */
