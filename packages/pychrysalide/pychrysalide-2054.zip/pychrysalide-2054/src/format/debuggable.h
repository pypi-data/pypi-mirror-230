
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debuggable.h - prototypes pour le support des formats de débogage
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


#ifndef _FORMAT_DEBUGGABLE_H
#define _FORMAT_DEBUGGABLE_H


#include <glib-object.h>



#define G_TYPE_DBG_FORMAT               g_debuggable_format_get_type()
#define G_DBG_FORMAT(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_debuggable_format_get_type(), GDbgFormat))
#define G_IS_DBG_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_debuggable_format_get_type()))
#define G_DBG_FORMAT_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DBG_FORMAT, GDbgFormatClass))
#define G_IS_DBG_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DBG_FORMAT))
#define G_DBG_FORMAT_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DBG_FORMAT, GDbgFormatClass))


/* Format de débogage générique (instance) */
typedef struct _GDbgFormat GDbgFormat;

/* Format de débogage générique (classe) */
typedef struct _GDbgFormatClass GDbgFormatClass;


/* Indique le type défini pour un format de débogage générique. */
GType g_debuggable_format_get_type(void);



#endif  /* _FORMAT_DEBUGGABLE_H */
