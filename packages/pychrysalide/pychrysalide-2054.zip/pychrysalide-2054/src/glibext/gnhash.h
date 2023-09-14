
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gnhash.h - prototype pour une nouvelle fonction offrant une empreinte constante
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


#ifndef _GLIBEXT_GNHASH_H
#define _GLIBEXT_GNHASH_H


#include <glib-object.h>



/* Convertit un pointeur en une empreinte constante. */
guint g_constant_hash(gconstpointer);



#endif  /* _GLIBEXT_GNHASH_H */
