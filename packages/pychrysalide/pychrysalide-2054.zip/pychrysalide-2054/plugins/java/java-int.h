
/* Chrysalide - Outil d'analyse de fichiers binaires
 * java-int.h - prototypes pour les structures internes du format Java
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


#ifndef _FORMAT_JAVA_JAVA_INT_H
#define _FORMAT_JAVA_JAVA_INT_H


#include "java.h"
#include "java_def.h"
#include "../executable-int.h"





/* Format d'exécutable Java (instance) */
struct _GJavaFormat
{
    GExeFormat parent;                      /* A laisser en premier        */

    java_header header;                     /* En-tête du programme        */

};

/* Format d'exécutable Java (classe) */
struct _GJavaFormatClass
{
    GExeFormatClass parent;                 /* A laisser en premier        */

};





/* Procède à la lecture d'une en-tête de programme Java. */
bool read_java_header(const GJavaFormat *, off_t *, java_header *);








#endif  /* _FORMAT_JAVA_JAVA_INT_H */
