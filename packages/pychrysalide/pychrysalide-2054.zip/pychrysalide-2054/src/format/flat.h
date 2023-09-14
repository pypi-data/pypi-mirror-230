
/* Chrysalide - Outil d'analyse de fichiers binaires
 * flat.h - prototypes pour le support des formats à plat
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


#ifndef _FORMAT_FLAT_H
#define _FORMAT_FLAT_H


#include <glib-object.h>


#include "executable.h"
#include "../analysis/content.h"



#define G_TYPE_FLAT_FORMAT            g_flat_format_get_type()
#define G_FLAT_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_FLAT_FORMAT, GFlatFormat))
#define G_IS_FLAT_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_FLAT_FORMAT))
#define G_FLAT_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_FLAT_FORMAT, GFlatFormatClass))
#define G_IS_FLAT_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_FLAT_FORMAT))
#define G_FLAT_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_FLAT_FORMAT, GFlatFormatClass))


/* Format d'exécutable à plat (instance) */
typedef struct _GFlatFormat GFlatFormat;

/* Format d'exécutable à plat (classe) */
typedef struct _GFlatFormatClass GFlatFormatClass;


/* Indique le type défini pour un format d'exécutable à plat. */
GType g_flat_format_get_type(void);

/* Prend en charge un nouveau format à plat. */
GExeFormat *g_flat_format_new(GBinContent *, const char *, SourceEndian);



#endif  /* _FORMAT_FLAT_H */
