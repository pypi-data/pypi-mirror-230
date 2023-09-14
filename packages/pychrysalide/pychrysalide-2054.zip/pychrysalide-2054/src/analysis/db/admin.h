
/* Chrysalide - Outil d'analyse de fichiers binaires
 * admin.h - prototypes pour la connexion en administrateur à un serveur Chrysalide
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


#ifndef _ANALYSIS_DB_ADMIN_H
#define _ANALYSIS_DB_ADMIN_H


#include <glib-object.h>
#include <stdbool.h>
#include <openssl/ssl.h>


#include "client.h"
#include "collection.h"
#include "misc/snapshot.h"



#define G_TYPE_ADMIN_CLIENT            g_admin_client_get_type()
#define G_ADMIN_CLIENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ADMIN_CLIENT, GAdminClient))
#define G_IS_ADMIN_CLIENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ADMIN_CLIENT))
#define G_ADMIN_CLIENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ADMIN_CLIENT, GAdminClientClass))
#define G_IS_ADMIN_CLIENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ADMIN_CLIENT))
#define G_ADMIN_CLIENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ADMIN_CLIENT, GAdminClientClass))


/* Description de client à l'écoute (instance) */
typedef struct _GAdminClient GAdminClient;

/* Description de client à l'écoute (classe) */
typedef struct _GAdminClientClass GAdminClientClass;


/* Indique le type défini pour une description de client à l'écoute. */
GType g_admin_client_get_type(void);

/* Prépare un client pour une connexion à une BD. */
GAdminClient *g_admin_client_new(void);

/* Effectue une demande de liste de binaires existants. */
bool g_admin_client_request_existing_binaries(GAdminClient *);

/* Fournit la liste des instantanés existants. */
char **g_admin_client_get_existing_binaries(GAdminClient *, size_t *);



#endif  /* _ANALYSIS_DB_ADMIN_H */
