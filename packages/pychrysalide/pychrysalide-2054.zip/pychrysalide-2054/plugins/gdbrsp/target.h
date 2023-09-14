
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target.h - prototypes pour la gestion des éléments propres à l'architecture reconnue par GDB
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


#ifndef _DEBUG_GDBRSP_TARGET_H
#define _DEBUG_GDBRSP_TARGET_H


#include <glib-object.h>
#include <stdbool.h>


#include "stream.h"
#include "../../common/endianness.h"



#define G_TYPE_GDB_TARGET            (g_gdb_target_get_type())
#define G_GDB_TARGET(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_GDB_TARGET, GGdbTarget))
#define G_IS_GDB_TARGET(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_GDB_TARGET))
#define G_GDB_TARGET_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GDB_TARGET, GGdbTargetClass))
#define G_IS_GDB_TARGET_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GDB_TARGET))
#define G_GDB_TARGET_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GDB_TARGET, GGdbTargetClass))


/* Indications quant à l'interfaçage client/serveur GDB (instance) */
typedef struct _GGdbTarget GGdbTarget;

/* Indications quant à l'interfaçage client/serveur GDB (classe) */
typedef struct _GGdbTargetClass GGdbTargetClass;


/* Indique le type défini par la GLib pour les détails d'interfaçage GDB. */
GType g_gdb_target_get_type(void);

/* Crée une définition des détails d'interfaçage GDB. */
GGdbTarget *g_gdb_target_new(GGdbStream *);

/* Liste l'ensemble des registres appartenant à un groupe. */
char **g_gdb_target_get_register_names(const GGdbTarget *, const char *, size_t *);

/* Indique la taille associée à un registre donné. */
unsigned int g_gdb_target_get_register_size(const GGdbTarget *, const char *);

/* Effectue la lecture d'un registre donné. */
bool g_gdb_target_read_register(GGdbTarget *, GGdbStream *, SourceEndian, const char *, size_t, ...);

/* Effectue l'écriture d'un registre donné. */
bool g_gdb_target_write_register(GGdbTarget *, GGdbStream *, SourceEndian, const char *, size_t, ...);



#endif  /* _DEBUG_GDBRSP_TARGET_H */
