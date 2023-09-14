
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend-int.h - prototypes internes pour le suivi d'une connexion à un serveur
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


#ifndef _ANALYSIS_DB_BACKEND_INT_H
#define _ANALYSIS_DB_BACKEND_INT_H


#include <stdbool.h>


#include "backend.h"



/* Prend en compte une connexion nouvelle d'un utilisateur. */
typedef void (* add_backend_client_fc) (GServerBackend *, SSL *, const char *, const char *);


/* Support pour un suivi de connexion à un serveur (instance) */
struct _GServerBackend
{
    GObject parent;                         /* A laisser en premier        */

    int stop_ctrl[2];                       /* Commande d'arrêt            */
    int refresh_ctrl[2];                    /* Commande d'actualisation    */
    GThread *process;                       /* Procédure de traitement     */

};

/* Support pour un suivi de connexion à un serveur (classe) */
struct _GServerBackendClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    const char *thread_name;                /* Désignation de processus    */
    GThreadFunc thread_func;                /* Traitement des échanges     */

    add_backend_client_fc add_client;       /* Intégration d'un client     */

};


/* Met fin à un support de suivi. */
void g_server_backend_stop(GServerBackend *);



#endif  /* _ANALYSIS_DB_BACKEND_INT_H */
