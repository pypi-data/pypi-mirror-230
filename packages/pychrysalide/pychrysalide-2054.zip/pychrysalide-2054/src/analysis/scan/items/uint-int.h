
/* Chrysalide - Outil d'analyse de fichiers binaires
 * uint-int.h - prototypes internes pour la lecture d'un mot à partir de données binaires
 *
 * Copyright (C) 2023 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_ITEMS_UINT_INT_H
#define _ANALYSIS_SCAN_ITEMS_UINT_INT_H


#include "uint.h"


#include "../item-int.h"



/* Fonction conduisant à la lecture d'un mot (instance) */
struct _GScanUintFunction
{
    GRegisteredItem parent;                 /* A laisser en premier        */

    MemoryDataSize size;                    /* Taille du mot à lire        */
    SourceEndian endian;                    /* Boutisme à respecter        */

};

/* Fonction conduisant à la lecture d'un mot (classe) */
struct _GScanUintFunctionClass
{
    GRegisteredItemClass parent;            /* A laisser en premier        */

};


/* Met en place un nouvelle fonction de lecture d'entiers. */
bool g_scan_uint_function_create(GScanUintFunction *, MemoryDataSize, SourceEndian);



#endif  /* _ANALYSIS_SCAN_ITEMS_UINT_INT_H */
