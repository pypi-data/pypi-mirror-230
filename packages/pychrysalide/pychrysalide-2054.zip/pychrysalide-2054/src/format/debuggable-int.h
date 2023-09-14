
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debuggable-int.h - prototypes utiles aux formats d'exécutables
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


#ifndef _FORMAT_DEBUGGABLE_INT_H
#define _FORMAT_DEBUGGABLE_INT_H


#include "debuggable.h"


#include "format-int.h"
#include "executable.h"



/* Format de débogage générique (instance) */
struct _GDbgFormat
{
    GBinFormat parent;                      /* A laisser en premier        */

    GExeFormat *executable;                 /* Binaire principal attaché   */

};

/* Format de débogage générique (classe) */
struct _GDbgFormatClass
{
    GBinFormatClass parent;                 /* A laisser en premier        */

};


/* Associe officiellement des formats exécutable et de débogage. */
void g_debuggable_format_attach_executable(GDbgFormat *, GExeFormat *);



#endif  /* _FORMAT_DEBUGGABLE_INT_H */
