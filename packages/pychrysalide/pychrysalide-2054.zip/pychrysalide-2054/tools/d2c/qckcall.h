
/* Chrysalide - Outil d'analyse de fichiers binaires
 * qckcall.h - prototypes pour un appel rapide et facilité à une fonction C de Chrysalide
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


#ifndef _TOOLS_D2C_QCKCALL_H
#define _TOOLS_D2C_QCKCALL_H


#include <stdbool.h>


#include "args/manager.h"
#include "bits/manager.h"
#include "conv/manager.h"



/* Prépare au besoin la définition d'une macro de transtypage. */
char *build_cast_if_needed(const char *);

/* Réalise un appel à une fonction liée à une instruction. */
bool call_instr_func(const char *, const arg_list_t *, int, const coding_bits *, const conv_list *);

/* Réalise un appel à une fonction liée à une instruction. */
bool checked_call_instr_func(const char *, const arg_list_t *, int, const coding_bits *, const conv_list *);



#endif  /* _TOOLS_D2C_QCKCALL_H */
