
/* Chrysalide - Outil d'analyse de fichiers binaires
 * controller.h - prototypes pour la gestion d'un ensemble d'archives au format CDB
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_CONTROLLER_H
#define _ANALYSIS_DB_CONTROLLER_H


#include <glib-object.h>
#include <stdbool.h>


#include "protocol.h"



#define G_TYPE_CDB_CONTROLLER            g_cdb_controller_get_type()
#define G_CDB_CONTROLLER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CDB_CONTROLLER, GCdbController))
#define G_IS_CDB_CONTROLLER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CDB_CONTROLLER))
#define G_CDB_CONTROLLER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CDB_CONTROLLER, GCdbControllerClass))
#define G_IS_CDB_CONTROLLER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CDB_CONTROLLER))
#define G_CDB_CONTROLLER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CDB_CONTROLLER, GCdbControllerClass))


/* Description d'un contrôleur d'archives (instance) */
typedef struct _GCdbController GCdbController;

/* Description d'un contrôleur d'archives (classe) */
typedef struct _GCdbControllerClass GCdbControllerClass;


/* Indique le type défini pour une gestion d'archives. */
GType g_cdb_controller_get_type(void);

/* Prépare un client pour une connexion à une BD. */
GCdbController *g_cdb_controller_new(const char *, DBError *);



#endif  /* _ANALYSIS_DB_CONTROLLER_H */
