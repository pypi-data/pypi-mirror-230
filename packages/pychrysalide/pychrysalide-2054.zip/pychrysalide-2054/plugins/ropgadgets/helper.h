
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helper.h - prototypes pour la recherche générique de gadgets
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _PLUGINS_ROPGADGETS_HELPER_H
#define _PLUGINS_ROPGADGETS_HELPER_H


#include <arch/processor.h>



/* Etablit une liste des contextes utiles à la recherche. */
size_t list_rop_contexts_by_default(char ***);

/* Etablit un contexte utile et adapté à une recherche. */
GProcContext *get_rop_contexts_by_default(const GArchProcessor *, size_t);

/* Définit les tailles possibles d'une instruction recherchée. */
const phys_t *setup_instruction_sizes_by_default(size_t *);



#endif  /* _PLUGINS_ROPGADGETS_HELPER_H */
