/* Chrysalide - Outil d'analyse de fichiers binaires
 * break-int.h - prototypes pour la définition générique interne des points d'arrêt
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


#ifndef _DEBUG_BREAK_INT_H
#define _DEBUG_BREAK_INT_H


#include "break.h"



/* Traçabilité des poses */
typedef struct _bp_source
{
    RawBpOrigin origin;                     /* Source de la définition     */

    /* Si origin != RBO_USER : */

    dbg_thread_id_t tid;                    /* Identifiant du thread lié   */
    virt_t previous;                        /* Arrêt officiel d'origine    */

} bp_source;


/* Définition d'un point d'arrêt appliqué */
struct _raw_breakpoint
{
    virt_t addr;                            /* Adresse d'application       */

    union
    {
        bp_source source;                   /* Origine du point d'arrêt    */
        bp_source *sources;                 /* Origines du point d'arrêt   */
    };
    size_t count;                           /* Nombre de ces origines      */

};


/* Initialise le coeur d'un point d'arrêt. */
void init_raw_breakpoint(raw_breakpoint *, virt_t);



#endif  /* _DEBUG_BREAK_INT_H */
