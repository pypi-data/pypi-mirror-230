
/* Chrysalide - Outil d'analyse de fichiers binaires
 * preload.c - préchargement d'instructions à partir d'un format
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


#ifndef _FORMAT_PRELOAD_INT_H
#define _FORMAT_PRELOAD_INT_H


#include "preload.h"


#include "../common/array.h"



/* Préchargement d'origine formatée (instance) */
struct _GPreloadInfo
{
    GObject parent;                         /* A laisser en premier        */

    flat_array_t *instructions;             /* Liste d'instructions        */
    flat_array_t *comments;                 /* Liste de commentaires       */

};

/* Préchargement d'origine formatée (classe) */
struct _GPreloadInfoClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _FORMAT_PRELOAD_INT_H */
