
/* Chrysalide - Outil d'analyse de fichiers binaires
 * field.h - prototypes pour la gestion des champs Java
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


#ifndef _FORMAT_JAVA_FIELD_H
#define _FORMAT_JAVA_FIELD_H


#include "e_java.h"



/* Charge les champs d'un binaire Java. */
bool load_java_fields(java_format *, off_t *);

/* Décharge les champs d'un binaire Java. */
void unload_java_fields(java_format *);



#endif  /* _FORMAT_JAVA_FIELD_H */
