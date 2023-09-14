
/* Chrysalide - Outil d'analyse de fichiers binaires
 * curl.h - prototypes pour l'encapsulation des fonctionnalités de cURL
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _COMMON_CURL_H
#define _COMMON_CURL_H


#include <stdbool.h>
#include <curl/curl.h>



/* Données échangées avec Internet */
typedef struct _curl_net_data_t
{
    char *memory;                           /* Zone de mémoire allouée     */
    size_t size;                            /* Quantité de données         */

} curl_net_data_t;


/* Prototype pour une intervention complémentaire dans la préparation des requêtes */
typedef CURLcode (* setup_extra_curl_cb) (CURL *);


/* Mémorise les données reçues en réponse à une requête. */
bool send_http_get_request(const char *, char * const [], size_t, const char *, setup_extra_curl_cb, curl_net_data_t *);

/* Mémorise les données reçues en réponse à une requête. */
bool send_http_post_request(const char *, char * const [], size_t, const char *, const curl_net_data_t *, setup_extra_curl_cb, curl_net_data_t *);



#endif  /* _COMMON_CURL_H */
