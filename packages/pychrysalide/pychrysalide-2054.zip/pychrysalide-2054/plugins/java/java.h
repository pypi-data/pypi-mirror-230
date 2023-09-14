
/* Chrysalide - Outil d'analyse de fichiers binaires
 * java.h - prototypes pour le support du format Java
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


#ifndef _FORMAT_JAVA_JAVA_H
#define _FORMAT_JAVA_JAVA_H


#include <glib-object.h>
#include <stdbool.h>
#include <sys/types.h>


#include "../../core/formats.h"



#define G_TYPE_JAVA_FORMAT            g_java_format_get_type()
#define G_JAVA_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_JAVA_FORMAT, GJavaFormat))
#define G_IS_JAVA_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_JAVA_FORMAT))
#define G_JAVA_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_JAVA_FORMAT, GJavaFormatClass))
#define G_IS_JAVA_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_JAVA_FORMAT))
#define G_JAVA_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_JAVA_FORMAT, GJavaFormatClass))


/* Format d'exécutable Java (instance) */
typedef struct _GJavaFormat GJavaFormat;

/* Format d'exécutable Java (classe) */
typedef struct _GJavaFormatClass GJavaFormatClass;


/* Indique si le format peut être pris en charge ici. */
bool java_is_matching(GBinContent *);

/* Indique le type défini pour un format d'exécutable Java. */
GType g_java_format_get_type(void);

/* Prend en charge un nouveau format Java. */
GBinFormat *g_java_format_new(const bin_t *, off_t);



#endif  /* _FORMAT_JAVA_JAVA_H */
