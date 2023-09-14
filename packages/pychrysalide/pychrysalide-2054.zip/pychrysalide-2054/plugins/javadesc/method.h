
/* Chrysalide - Outil d'analyse de fichiers binaires
 * shorty.h - prototypes pour le décodage de routines pour Java
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


#ifndef _PLUGINS_JAVADESC_SHORTY_H
#define _PLUGINS_JAVADESC_SHORTY_H


#include <analysis/routine.h>
#include <common/ibuf.h>



/* Extrait un routine particulière depuis un codage Java. */
GBinRoutine *jmd_method_descriptor(input_buffer *);



#endif  /* _PLUGINS_JAVADESC_SHORTY_H */
