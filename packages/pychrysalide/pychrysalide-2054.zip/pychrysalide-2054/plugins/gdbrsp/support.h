
/* Chrysalide - Outil d'analyse de fichiers binaires
 * support.h - prototypes pour la conformité dans l'interfaçage client/serveur
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


#ifndef _DEBUG_GDBRSP_SUPPORT_H
#define _DEBUG_GDBRSP_SUPPORT_H


#include <glib-object.h>
#include <stdbool.h>


#include "stream.h"



#define G_TYPE_GDB_SUPPORT            (g_gdb_support_get_type())
#define G_GDB_SUPPORT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_GDB_SUPPORT, GGdbSupport))
#define G_IS_GDB_SUPPORT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_GDB_SUPPORT))
#define G_GDB_SUPPORT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GDB_SUPPORT, GGdbSupportClass))
#define G_IS_GDB_SUPPORT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GDB_SUPPORT))
#define G_GDB_SUPPORT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GDB_SUPPORT, GGdbSupportClass))


/* Indications quant à l'interfaçage client/serveur GDB (instance) */
typedef struct _GGdbSupport GGdbSupport;

/* Indications quant à l'interfaçage client/serveur GDB (classe) */
typedef struct _GGdbSupportClass GGdbSupportClass;


/* Indique le type défini par la GLib pour les détails d'interfaçage GDB. */
GType g_gdb_support_get_type(void);

/* Crée une définition des détails d'interfaçage GDB. */
GGdbSupport *g_gdb_support_new(GGdbStream *);







char *g_gdb_support_get_id(const GGdbSupport *support);









#endif  /* _DEBUG_GDBRSP_SUPPORT_H */
