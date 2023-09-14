
/* Chrysalide - Outil d'analyse de fichiers binaires
 * curl.c - encapsulation des fonctionnalités de cURL
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


#include "curl.h"


#include <malloc.h>
#include <string.h>



/* Mémorise les données reçues en réponse à une requête. */
static size_t receive_data_from_internet(void *, size_t, size_t, curl_net_data_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : contents = contenu nouveau en arrivance d'Internet.          *
*                size     = taille d'un élément reçu.                         *
*                nmemb    = quantité de ces éléments.                         *
*                data     = zone de collecte à compléter. [OUT]               *
*                                                                             *
*  Description : Mémorise les données reçues en réponse à une requête.        *
*                                                                             *
*  Retour      : Taille de données effectivement reçue.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t receive_data_from_internet(void *contents, size_t size, size_t nmemb, curl_net_data_t *data)
{
    size_t realsize;                        /* Taille brute en octets      */

    realsize = size * nmemb;

    data->memory = realloc(data->memory, data->size + realsize + 1);

    memcpy(&(data->memory[data->size]), contents, realsize);

    data->size += realsize;

    data->memory[data->size] = 0;

    return realsize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : url     = resource distant à cibler.                         *
*                headers = entêtes enventuels à joindre à la requête.         *
*                hcount  = quantité de ces entêtes.                           *
*                cookies = éventuels biscuits formatés ou NULL.               *
*                ecb     = éventuelle fonction d'intervention à appeler.      *
*                resp    = réponse obtenue du serveur distant. [OUT]          *
*                                                                             *
*  Description : Mémorise les données reçues en réponse à une requête.        *
*                                                                             *
*  Retour      : Taille de données effectivement reçue.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool send_http_get_request(const char *url, char * const headers[], size_t hcount, const char *cookies, setup_extra_curl_cb ecb, curl_net_data_t *resp)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    CURL *req;                              /* Requête HTTP                */
    struct curl_slist *hlist;               /* Entêtes éventuelles         */
    size_t i;                               /* Boucle de parcours          */
    CURLcode ret;                           /* Code de retour d'opération  */

    result = false;

    resp->memory = NULL;
    resp->size = 0;

    req = curl_easy_init();
    if (req == NULL) goto exit;

    curl_easy_setopt(req, CURLOPT_URL, url);

    /* Entêtes à transmettre */

    hlist = NULL;

    for (i = 0; i < hcount; i++)
        hlist = curl_slist_append(hlist, headers[i]);

    curl_easy_setopt(req, CURLOPT_HTTPHEADER, hlist);

    if (cookies != NULL)
        curl_easy_setopt(req, CURLOPT_COOKIE, cookies);

    /* Réception des données */

    curl_easy_setopt(req, CURLOPT_WRITEDATA, (void *)resp);

    curl_easy_setopt(req, CURLOPT_WRITEFUNCTION, receive_data_from_internet);

    /* Définition de la charge utile */

    curl_easy_setopt(req, CURLOPT_HTTPGET, 1);

    /* Emission de la requête */

    if (ecb != NULL)
        ecb(req);

    ret = curl_easy_perform(req);

    result = (ret == CURLE_OK);

    if (!result)
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(ret));

    curl_slist_free_all(hlist);

    curl_easy_cleanup(req);

 exit:

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : url     = resource distant à cibler.                         *
*                headers = entêtes enventuels à joindre à la requête.         *
*                hcount  = quantité de ces entêtes.                           *
*                cookies = éventuels biscuits formatés ou NULL.               *
*                payload = charge utile à transmettre au serveur distant.     *
*                ecb     = éventuelle fonction d'intervention à appeler.      *
*                resp    = réponse obtenue du serveur distant. [OUT]          *
*                                                                             *
*  Description : Mémorise les données reçues en réponse à une requête.        *
*                                                                             *
*  Retour      : Taille de données effectivement reçue.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool send_http_post_request(const char *url, char * const headers[], size_t hcount, const char *cookies, const curl_net_data_t *payload, setup_extra_curl_cb ecb, curl_net_data_t *resp)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    CURL *req;                              /* Requête HTTP                */
    struct curl_slist *hlist;               /* Entêtes éventuelles         */
    size_t i;                               /* Boucle de parcours          */
    CURLcode ret;                           /* Code de retour d'opération  */

    result = false;

    resp->memory = NULL;
    resp->size = 0;

    req = curl_easy_init();
    if (req == NULL) goto exit;

    curl_easy_setopt(req, CURLOPT_URL, url);

    /* Entêtes à transmettre */

    hlist = NULL;

    for (i = 0; i < hcount; i++)
        hlist = curl_slist_append(hlist, headers[i]);

    curl_easy_setopt(req, CURLOPT_HTTPHEADER, hlist);

    if (cookies != NULL)
        curl_easy_setopt(req, CURLOPT_COOKIE, cookies);

    /* Réception des données */

    curl_easy_setopt(req, CURLOPT_WRITEDATA, (void *)resp);

    curl_easy_setopt(req, CURLOPT_WRITEFUNCTION, receive_data_from_internet);

    /* Définition de la charge utile */

    curl_easy_setopt(req, CURLOPT_POST, 1);

    curl_easy_setopt(req, CURLOPT_POSTFIELDS, payload->memory);
    curl_easy_setopt(req, CURLOPT_POSTFIELDSIZE, payload->size);

    /* Emission de la requête */

    if (ecb != NULL)
        ecb(req);

    ret = curl_easy_perform(req);

    result = (ret == CURLE_OK);

    if (!result)
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(ret));

    curl_slist_free_all(hlist);

    curl_easy_cleanup(req);

 exit:

    return result;

}
