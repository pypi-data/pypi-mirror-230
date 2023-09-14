
/* Chrysalide - Outil d'analyse de fichiers binaires
 * client.h - prototypes pour la connexion à un serveur Chrysalide
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


#ifndef _ANALYSIS_DB_CLIENT_INT_H
#define _ANALYSIS_DB_CLIENT_INT_H


#include "client.h"


#include "../../common/packed.h"



/* Termine la constitution des données initiales à présenter. */
typedef bool (* complete_client_hello_fc) (GHubClient *, packed_buffer_t *);


/* Description de client à l'écoute (instance) */
struct _GHubClient
{
    GObject parent;                         /* A laisser en premier        */

    char *working;                          /* Répertoire de travail       */

    SSL_CTX *tls_ctx;                       /* Contexte du chiffrement     */

    int fd;                                 /* Canal de communication      */
    SSL *tls_fd;                            /* Même canal, mais sécurisé   */
    char *desc;                             /* Description du lien         */

    GMutex sending_lock;                    /* Concurrence des envois      */
    int stop_ctrl[2];                       /* Commande d'arrêt            */
    GThread *update;                        /* Procédure de traitement     */

};

/* Description de client à l'écoute (classe) */
struct _GHubClientClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    uint32_t role;                          /* Rôle associé aux clients    */
    complete_client_hello_fc complete_hello;/* Finalisation de l'intro     */
    GThreadFunc recv_func;                  /* Réception de données        */

};



/* Identifie le canal de communication pour envois au serveur. */
SSL *g_hub_client_get_ssl_fd(GHubClient *);

/* Marque le canal de communication comme disponible. */
void g_hub_client_put_ssl_fd(GHubClient *, SSL *);



#endif  /* _ANALYSIS_DB_CLIENT_INT_H */
