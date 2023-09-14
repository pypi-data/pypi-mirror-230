
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helper_arm.h - prototypes pour la gestion auxiliaire de l'architecture ARM
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


#ifndef _PLUGINS_ELF_HELPER_ARM_H
#define _PLUGINS_ELF_HELPER_ARM_H


#include "format.h"



/* Fournit la description humaine d'un type de segment ELF. */
const char *get_elf_program_arm_type_desc(uint32_t);

/* Fournit une adresse virtuelle prête à emploi. */
virt_t fix_elf_arm_virtual_address(virt_t);

/* Détermine l'emplacement de la première entrée dans la PLT. */
bool find_first_plt_entry(GElfFormat *, vmpa2t *);

/* Retrouve le décalage appliqué lors d'une résolution. */
bool retrieve_arm_linkage_offset(GElfFormat *, vmpa2t *, uint64_t *);



#endif  /* _PLUGINS_ELF_HELPER_ARM_H */
