
/* Chrysalide - Outil d'analyse de fichiers binaires
 * e_java.h - prototypes pour le support du format Java
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


#ifndef _FORMAT_JAVA_E_JAVA_H
#define _FORMAT_JAVA_E_JAVA_H


#include "../exe_format.h"


/* Description des attributs Java */
typedef struct _java_attribute java_attribute;

/* Description du format Java */
typedef struct _java_format java_format;


/* Indique si le format peut être pris en charge ici. */
bool java_is_matching(const uint8_t *, off_t);

/* Prend en charge une nouvelle classe Java. */
exe_format *load_java(const uint8_t *, off_t);

/* Efface la prise en charge une nouvelle classe Java. */
void unload_java(java_format *);



#endif  /* _FORMAT_JAVA_E_JAVA_H */
