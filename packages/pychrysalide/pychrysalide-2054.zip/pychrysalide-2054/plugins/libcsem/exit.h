
/* Chrysalide - Outil d'analyse de fichiers binaires
 * exit.h - prototypes pour la définition des sorties comme points de non retour
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


#ifndef _PLUGINS_LIBCSEM_EXIT_H
#define _PLUGINS_LIBCSEM_EXIT_H


#include <analysis/binary.h>



/* Modifie toutes les instructions appelant exit(). */
void mark_exit_calls_as_return_instructions(const GLoadedBinary *);



#endif  /* _PLUGINS_LIBCSEM_EXIT_H */
