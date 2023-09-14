
/* Chrysalide - Outil d'analyse de fichiers binaires
 * flat-int.h - prototypes de code utile aux formats d'exécutables à plat
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


#ifndef _FORMAT_FLAT_INT_H
#define _FORMAT_FLAT_INT_H


#include "flat.h"


#include "executable-int.h"



/* Format d'exécutable à plat (instance) */
struct _GFlatFormat
{
    GExeFormat parent;                      /* A laisser en premier        */

    char *machine;                          /* Architecture imposée        */
    SourceEndian endian;                    /* Boutisme imposé             */

};

/* Format d'exécutable à plat (classe) */
struct _GFlatFormatClass
{
    GExeFormatClass parent;                 /* A laisser en premier        */

};



#endif  /* _FORMAT_FLAT_INT_H */
