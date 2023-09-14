
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend.h - prototypes pour le suivi d'une connexion à un serveur
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_BACKEND_H
#define _ANALYSIS_DB_BACKEND_H


#include <glib-object.h>
#include <openssl/ssl.h>



#define G_TYPE_SERVER_BACKEND            g_server_backend_get_type()
#define G_SERVER_BACKEND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SERVER_BACKEND, GServerBackend))
#define G_IS_SERVER_BACKEND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SERVER_BACKEND))
#define G_SERVER_BACKEND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SERVER_BACKEND, GServerBackendClass))
#define G_IS_SERVER_BACKEND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SERVER_BACKEND))
#define G_SERVER_BACKEND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SERVER_BACKEND, GServerBackendClass))


/* Support pour un suivi de connexion à un serveur (instance) */
typedef struct _GServerBackend GServerBackend;

/* Support pour un suivi de connexion à un serveur (classe) */
typedef struct _GServerBackendClass GServerBackendClass;


/* Indique le type défini pour un Support de suivi de connexion. */
GType g_server_backend_get_type(void);

/* Prend en compte une connexion nouvelle d'un utilisateur. */
void g_server_backend_add_client(GServerBackend *, SSL *, const char *);



#endif  /* _ANALYSIS_DB_BACKEND_H */
