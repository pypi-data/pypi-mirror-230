
/* Chrysalide - Outil d'analyse de fichiers binaires
 * server.h - prototypes pour la mise en place d'un fournisseur d'éléments ajoutés
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


#ifndef _ANALYSIS_DB_SERVER_H
#define _ANALYSIS_DB_SERVER_H


#include <glib-object.h>
#include <stdbool.h>



#define G_TYPE_HUB_SERVER            g_hub_server_get_type()
#define G_HUB_SERVER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_HUB_SERVER, GHubServer))
#define G_IS_HUB_SERVER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_HUB_SERVER))
#define G_HUB_SERVER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_HUB_SERVER, GHubServerClass))
#define G_IS_HUB_SERVER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_HUB_SERVER))
#define G_HUB_SERVER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_HUB_SERVER, GHubServerClass))


/* Description de serveur à l'écoute (instance) */
typedef struct _GHubServer GHubServer;

/* Description de serveur à l'écoute (classe) */
typedef struct _GHubServerClass GHubServerClass;


/* Indique le type défini pour une description de serveur à l'écoute. */
GType g_hub_server_get_type(void);

/* Prépare un serveur de BD pour les clients internes. */
GHubServer *g_hub_server_new_internal(void);

/* Prépare un serveur de BD pour les clients distants. */
GHubServer *g_hub_server_new_remote(const char *, const char *, bool);

/* Bilan du lancement d'un serveur */
typedef enum _ServerStartStatus
{
    SSS_FAILURE,                            /* Echec du démarrage          */
    SSS_SUCCESS,                            /* Serveur démarré             */
    SSS_ALREADY_RUNNING,                    /* Instance déjà en place      */

} ServerStartStatus;

/* Démarre le serveur de base de données. */
ServerStartStatus g_hub_server_start(GHubServer *, int, bool);

/* Attend l'arrête du serveur de base de données. */
void g_hub_server_wait_for_stop(GHubServer *);

/* Arrête le serveur de base de données. */
void g_hub_server_stop(GHubServer *);



#endif  /* _ANALYSIS_DB_SERVER_H */
