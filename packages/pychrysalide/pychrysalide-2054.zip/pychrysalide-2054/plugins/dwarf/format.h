
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dwarf.h - prototypes pour le support du format Dwarf
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


#ifndef _PLUGINS_DWARF_FORMAT_H
#define _PLUGINS_DWARF_FORMAT_H


#include <glib-object.h>


#include <format/debuggable.h>
#include <format/executable.h>


#include "def.h"



#define G_TYPE_DWARF_FORMAT            g_dwarf_format_get_type()
#define G_DWARF_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DWARF_FORMAT, GDwarfFormat))
#define G_IS_DWARF_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DWARF_FORMAT))
#define G_DWARF_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DWARF_FORMAT, GDwarfFormatClass))
#define G_IS_DWARF_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DWARF_FORMAT))
#define G_DWARF_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DWARF_FORMAT, GDwarfFormatClass))


/* Format de débogage DWARF (instance) */
typedef struct _GDwarfFormat GDwarfFormat;

/* Format de débogage DWARF (classe) */
typedef struct _GDwarfFormatClass GDwarfFormatClass;


/* Valide un contenu comme étant un format Dwarf. */
GDbgFormat *check_dwarf_format(GExeFormat *);

/* Indique le type défini pour un format de débogage DWARF. */
GType g_dwarf_format_get_type(void);

/* Prend en charge un nouveau format DWARF. */
GDbgFormat *g_dwarf_format_new(GExeFormat *);



#endif  /* _PLUGINS_DWARF_FORMAT_H */
