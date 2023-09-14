
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers_arm64.h - prototypes pour les compléments utiles à GDB pour l'architecture AArch64
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


#ifndef _DEBUG_GDBRSP_HELPERS_ARM64_H
#define _DEBUG_GDBRSP_HELPERS_ARM64_H


#include "gdb.h"



/* Remonte la pile d'appels jusqu'au point courant. */
bool compute_call_stack_for_arm64(GGdbDebugger *, virt_t **, size_t *);

/* Complète la commande manipulant des points d'arrêt. */
bool fill_memory_breakpoint_cmd_for_arm64(GGdbDebugger *, virt_t, char *);



#endif  /* _DEBUG_GDBRSP_HELPERS_ARM64_H */
