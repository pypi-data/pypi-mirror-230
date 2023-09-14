
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf_def_arm.h - liste des structures et constantes utilisées par le format ELF et dédiées à ARM
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


#ifndef _PLUGINS_ELF_ELF_DEF_ARM_H
#define _PLUGINS_ELF_ELF_DEF_ARM_H


#include "elf_def.h"



/* Valeurs spécifiques pour le champ p_type des en-tête de programme */

#define PT_ARM_EXIDX (PT_LOPROC + 1)        /* ARM unwind segment          */


/* Valeurs spécifiques pour le champ sh_type des en-têtes de section */

#define SHT_ARM_EXIDX      (SHT_LOPROC + 1) /* ARM unwind section          */
#define SHT_ARM_PREEMPTMAP (SHT_LOPROC + 2) /* Preemption details          */
#define SHT_ARM_ATTRIBUTES (SHT_LOPROC + 3) /* ARM attributes section      */



#endif  /* _PLUGINS_ELF_ELF_DEF_ARM_H */
