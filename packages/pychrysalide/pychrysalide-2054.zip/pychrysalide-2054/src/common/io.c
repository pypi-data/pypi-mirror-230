
/* Chrysalide - Outil d'analyse de fichiers binaires
 * io.c - entrées sorties fiables
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


#include "io.h"


#include <errno.h>
#include <fcntl.h>
#include <libgen.h>
#include <malloc.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>


#include "../core/logs.h"
#include "../core/params.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : fd    = flux ouvert en lecture.                              *
*                buf   = données à recevoir.                                  *
*                count = quantité de ces données.                             *
*                                                                             *
*  Description : Lit des données depuis un flux local.                        *
*                                                                             *
*  Retour      : true si toutes les données ont été lues, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool safe_read(int fd, void *buf, size_t count)
{
    uint8_t *iter;                          /* Données en attente          */
    size_t remaining;                       /* Quantité restante           */
    ssize_t got;                            /* Données envoyées            */

    iter = (uint8_t *)buf;
    remaining = count;

    while (remaining > 0)
    {
        got = read(fd, iter, remaining);

        if (got == -1)
        {
            if (errno == EINTR) continue;
            else
            {
                perror("read");
                break;
            }
        }

        if (got == 0)
            break;

        iter += got;
        remaining -= got;

    }

    return (remaining == 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd  = flux ouvert en lecture.                                *
*                buf = données à recevoir.                                    *
*                max = quantité maximale de ces données.                      *
*                                                                             *
*  Description : Lit des données depuis un flux local.                        *
*                                                                             *
*  Retour      : Nombre d'octets lus, au pire 0 en cas d'erreur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ssize_t safe_read_partial(int fd, void *buf, size_t max)
{
    ssize_t result;                         /* Quantité lue à remonter     */
    uint8_t *iter;                          /* Données en attente          */
    size_t remaining;                       /* Quantité restante           */
    ssize_t got;                            /* Données envoyées            */

    result = 0;

    iter = (uint8_t *)buf;
    remaining = max;

    while (remaining > 0)
    {
        got = read(fd, iter, remaining);

        if (got == -1)
        {
            if (errno == EINTR) continue;
            else
            {
                perror("read");
                break;
            }
        }

        if (got == 0)
            break;

        result += got;

        iter += got;
        remaining -= got;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fd    = flux ouvert en écriture.                             *
*                buf   = données à émettre.                                   *
*                count = quantité de ces données.                             *
*                                                                             *
*  Description : Ecrit des données dans un flux local.                        *
*                                                                             *
*  Retour      : true si toutes les données ont été écrites, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool safe_write(int fd, const void *buf, size_t count)
{
    uint8_t *iter;                          /* Données en attente          */
    size_t remaining;                       /* Quantité restante           */
    ssize_t sent;                           /* Données envoyées            */

    iter = (uint8_t *)buf;
    remaining = count;

    while (remaining > 0)
    {
        sent = write(fd, iter, remaining);

        if (sent == -1)
        {
            if (errno == EINTR) continue;
            else
            {
                perror("write");
                break;
            }
        }

        if (sent == 0)
            break;

        iter += sent;
        remaining -= sent;

    }

    return (remaining == 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sockfd = flux ouvert en lecture.                             *
*                buf    = données à recevoir.                                 *
*                len    = quantité de ces données.                            *
*                flags  = options de réception.                               *
*                                                                             *
*  Description : Réceptionne des données depuis un flux réseau.               *
*                                                                             *
*  Retour      : true si toutes les données ont été reçues, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool safe_recv(int sockfd, void *buf, size_t len, int flags)
{
    uint8_t *iter;                          /* Données en attente          */
    size_t remaining;                       /* Quantité restante           */
    ssize_t got;                            /* Données envoyées            */

    iter = buf;
    remaining = len;

    while (remaining > 0)
    {
        got = recv(sockfd, iter, remaining, MSG_NOSIGNAL | flags);
        if (got == -1)
        {
            if (errno == EINTR) continue;
            else
            {
                perror("recv");
                break;
            }
        }

        iter += got;
        remaining -= got;

    }

    return (remaining == 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sockfd = flux ouvert en écriture.                            *
*                buf    = données à émettre.                                  *
*                len    = quantité de ces données.                            *
*                flags  = options d'envoi.                                    *
*                                                                             *
*  Description : Envoie des données au travers un flux réseau.                *
*                                                                             *
*  Retour      : true si toutes les données ont été émises, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool safe_send(int sockfd, const void *buf, size_t len, int flags)
{
    uint8_t *iter;                          /* Données en attente          */
    size_t remaining;                       /* Quantité restante           */
    ssize_t sent;                           /* Données envoyées            */

    iter = (uint8_t *)buf;
    remaining = len;

    while (remaining > 0)
    {
        sent = send(sockfd, iter, remaining, MSG_NOSIGNAL | flags);
        if (sent == -1)
        {
            if (errno == EINTR) continue;
            else
            {
                perror("send");
                break;
            }
        }

        iter += sent;
        remaining -= sent;

    }

    return (remaining == 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'accès à valider.                             *
*                                                                             *
*  Description : S'assure qu'un chemin donné existe dans le système.          *
*                                                                             *
*  Retour      : 0 si le chemin est actuellement présent, -1 sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int ensure_path_exists(const char *path)
{
    int result;                             /* Bilan de l'assurance        */
    char *copy;                             /* Chemin libérable            */
    char *tmp;                              /* Chemin altérable            */

    copy = strdup(path);
    tmp = dirname(copy);

    result = access(tmp, W_OK | X_OK);

    if (result != 0)
    {
        result = ensure_path_exists(tmp);

        if (result == 0)
            result = mkdir(tmp, 0700);

    }

    free(copy);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : prefix   = préfixe du nom du fichier temporaire à créer.     *
*                suffix   = éventuel suffixe à coller au nom de fichier.      *
*                filename = chemin d'accès complet au nouveau fichier. [OUT]  *
*                                                                             *
*  Description : Met en place un fichier temporaire.                          *
*                                                                             *
*  Retour      : Flux ouvert en lecture et écriture, ou -1 en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int make_tmp_file(const char *prefix, const char *suffix, char **filename)
{
    int result;                             /* Flux ou code à retourner    */
    const char *tmpdir;                     /* Répertoire d'accueil        */
    bool status;                            /* Bilan d'un consultation     */
    size_t slen;                            /* Taille du suffixe           */

    status = g_generic_config_get_value(get_main_configuration(), MPK_TMPDIR, &tmpdir);
    if (!status) return -1;

    slen = strlen(suffix);

    if (slen > 0)
        asprintf(filename, "%s" G_DIR_SEPARATOR_S "%s-%d.XXXXXX.%s", tmpdir, prefix, getpid(), suffix);
    else
        asprintf(filename, "%s" G_DIR_SEPARATOR_S "%s-%d.XXXXXX", tmpdir, prefix, getpid());

    result = ensure_path_exists(*filename);

    if (result == 0)
    {
        if (slen > 0)
            result = mkstemps(*filename, slen + 1);
        else
            result = mkstemp(*filename);

        if (result == -1) perror("mkstemp");

    }

    if (result == -1)
    {
        free(*filename);
        *filename = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = fichier de destination de la copie.                   *
*                src  = fichier source à copier.                              *
*                                                                             *
*  Description : Copie un fichier.                                            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool copy_file(const char *dest, const char *src)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Descripteur du fichier      */
    struct stat info;                       /* Informations sur le fichier */
    int ret;                                /* Bilan d'un appel            */
    void *data;                             /* Quantité de données traitées*/
    bool status;                            /* Bilan de la lecture         */

    result = false;

    /* Côté source */

    fd = open(src, O_RDONLY);
    if (fd == -1)
    {
        LOG_ERROR_N("open");
        goto exit;
    }

    ret = fstat(fd, &info);
    if (ret == -1)
    {
        LOG_ERROR_N("fstat");
        goto done;
    }

    data = malloc(info.st_size);

    status = safe_read(fd, data, info.st_size);
    if (!status) goto clean;

    close(fd);

    /* Côté destination */

    fd = open(dest, O_WRONLY | O_CREAT, S_IRUSR | S_IWUSR);
    if (fd == -1)
    {
        LOG_ERROR_N("open");
        free(data);
        goto exit;
    }

    status = safe_write(fd, data, info.st_size);
    if (!status) goto clean;

    result = true;

 clean:

    free(data);

 done:

    close(fd);

 exit:

    return result;

}
