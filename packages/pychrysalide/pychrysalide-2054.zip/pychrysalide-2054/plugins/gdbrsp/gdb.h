
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gdb.h - prototypes pour le débogage à l'aide de gdb.
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


#ifndef _DEBUG_GDBRSP_GDB_H
#define _DEBUG_GDBRSP_GDB_H


#include <glib-object.h>


#include "../debugger.h"



#define G_TYPE_GDB_DEBUGGER            (g_gdb_debugger_get_type())
#define G_GDB_DEBUGGER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_GDB_DEBUGGER, GGdbDebugger))
#define G_IS_GDB_DEBUGGER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_GDB_DEBUGGER))
#define G_GDB_DEBUGGER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GDB_DEBUGGER, GGdbDebuggerClass))
#define G_IS_GDB_DEBUGGER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GDB_DEBUGGER))
#define G_GDB_DEBUGGER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GDB_DEBUGGER, GGdbDebuggerClass))


/* Débogueur utilisant un serveur GDB (instance) */
typedef struct _GGdbDebugger GGdbDebugger;

/* Débogueur utilisant un serveur GDB (classe) */
typedef struct _GGdbDebuggerClass GGdbDebuggerClass;


/* Indique le type défini par la GLib pour le débogueur gdb. */
GType g_gdb_debugger_get_type(void);

/* Crée un débogueur utilisant un serveur GDB distant. */
GBinaryDebugger *g_gdb_debugger_new(GLoadedBinary *, const char *, unsigned short);


void test_gdb(void);



#endif  /* _DEBUG_GDBRSP_GDB_H */
