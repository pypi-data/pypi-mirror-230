
/* Chrysalide - Outil d'analyse de fichiers binaires
 * aops.h - prototypes pour les compléments utiles à GDB pour l'architecture ARM
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


#ifndef _DEBUG_GDBRSP_AOPS_H
#define _DEBUG_GDBRSP_AOPS_H


#include "gdb.h"



/* Détermine le point d'exécution courant. */
typedef bool (* get_pc_fc) (GGdbDebugger *, virt_t *);

/* Remonte la pile d'appels jusqu'au point courant. */
typedef bool (* compute_call_stack_fc) (const GGdbDebugger *, virt_t **, size_t *);

/* Complète la commande manipulant des points d'arrêt. */
typedef const char * (* get_bp_kind_fc) (const GGdbDebugger *, virt_t);

/* Construit une instruction provoquant un arrêt d'exécution. */
typedef const uint8_t * (* get_bp_data_fc) (const GGdbDebugger *, virt_t, size_t *);


/* Procédures spécifiques pour une architecture */
typedef struct _gdb_arch_ops
{
    get_pc_fc get_pc;                       /* Obtention du point d'exéc.  */
    compute_call_stack_fc compute_cstack;   /* Calcule la pile d'appels    */
    get_bp_kind_fc get_bp_kind;             /* Fournit le type d'un point  */
    get_bp_data_fc get_bp_data;             /* Code d'un point d'arrêt     */

} gdb_arch_ops;



#endif  /* _DEBUG_GDBRSP_AOPS_H */
