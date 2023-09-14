
/* Chrysalide - Outil d'analyse de fichiers binaires
 * break.h - prototypes pour la manipulation des points d'arrêt
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _DEBUG_BREAK_H
#define _DEBUG_BREAK_H


#include "misc.h"
#include "../arch/vmpa.h"



/* Origine des points d'arrêt en place */
typedef enum _RawBpOrigin
{
    RBO_INVALID  = (0 << 0),                /* Existance illégale          */
    RBO_USER     = (1 << 0),                /* Point d'arrêt utilisateur   */
    //RBO_COMPUTED = (1 << 1),                /* Arrêt sur un point spécial  */
    RBO_INTERNAL = (1 << 2),                /* Restauration transparente   */
    RBO_STEP     = (1 << 3),                /* Mise en place éphémère      */

    RBO_COUNT

} RawBpOrigin;


/* Définition d'un point d'arrêt appliqué */
typedef struct _raw_breakpoint raw_breakpoint;


/* Libère le coeur d'un point d'arrêt. */
void fini_raw_breakpoint(raw_breakpoint *);

/* Indique l'adresse du point d'arrêt dans la mémoire ciblée. */
virt_t get_raw_breakpoint_addr(const raw_breakpoint *);

/* Fournit l'adresse d'origine d'un point d'arrêt de pas à pas. */
virt_t get_raw_breakpoint_prev_addr(const raw_breakpoint *);

/* Effectue une comparaison entre adresse et point d'arrêt. */
int compare_raw_breakpoint_with_addr(const virt_t *, const raw_breakpoint **);

/* Effectue une comparaison entre deux points d'arrêt. */
int compare_raw_breakpoints(const raw_breakpoint **, const raw_breakpoint **);

/* Enregistre la source d'un point d'arrêt posé. */
void set_raw_breakpoint_origin(raw_breakpoint *, RawBpOrigin, dbg_thread_id_t, virt_t);

/* Oublie la source d'un point d'arrêt posé. */
void unset_raw_breakpoint_origin(raw_breakpoint *, RawBpOrigin, dbg_thread_id_t);

/* Indique si le point d'arrêt correspond à une source donnée. */
bool has_raw_breakpoint_origin(const raw_breakpoint *, RawBpOrigin, dbg_thread_id_t);

/* Indique si le point d'arrêt correspond à une origine donnée. */
bool has_raw_breakpoint_previous_address(const raw_breakpoint *, RawBpOrigin, dbg_thread_id_t, virt_t);

/* Indique si un point d'arrêt a encore une utilité. */
bool is_breakpoint_useless(const raw_breakpoint *);



#endif  /* _DEBUG_BREAK_H */
