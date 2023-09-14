
/* Chrysalide - Outil d'analyse de fichiers binaires
 * auth.h - prototypes pour la mise en place et gestion des autorisations pour les partages
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_AUTH_H
#define _ANALYSIS_DB_AUTH_H


#include <stdbool.h>
#include <sys/un.h>


#include "certs.h"
#include "protocol.h"


/* Met en place un canal UNIX pour un serveur interne. */
bool build_internal_server_socket(struct sockaddr_un *);

/* Fournit le répertoire de travail pour les données d'analyse. */
char *get_db_working_directory(const char *, const char *, const char *, const char *);

/* Détermine la désignation par défaut de l'usager. */
char *get_default_username(void);

/* Etablit une base pour l'identité de l'utilisateur. */
bool setup_client_identity(unsigned long, x509_entries *);

/* Etablit une base pour l'identité d'un serveur. */
bool setup_server_identity(const char *, const char *, unsigned long, x509_entries *);

/* Ajoute un certificat dans les utilisateurs d'un serveur. */
bool add_client_to_server(const char *, const char *, unsigned long, const char *, const char *);




/* Assure la présence d'unenvironnement pour serveur interne. */
bool ensure_internal_connections_setup(void);

/* Lance un serveur interne si besoin est. */
bool launch_internal_server(void);



#endif  /* _ANALYSIS_DB_AUTH_H */
