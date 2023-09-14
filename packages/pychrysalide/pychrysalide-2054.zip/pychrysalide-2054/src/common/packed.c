
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packed.c - regroupement de bribes de paquets réseau
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "packed.h"


#include <assert.h>
#include <endian.h>
#include <malloc.h>
#include <string.h>


#include "../core/logs.h"



/* Taille d'allocation en cas de besoin */
#define PACKET_BLOCK_SIZE 1000



/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à initialiser. [OUT]                *
*                                                                             *
*  Description : Initialise un paquet réseau pour une constitution.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_packed_buffer(packed_buffer_t *pbuf)
{
    pbuf->allocated = PACKET_BLOCK_SIZE;
    pbuf->data = malloc(pbuf->allocated * sizeof(uint8_t));

    reset_packed_buffer(pbuf);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à réinitialiser. [OUT]              *
*                                                                             *
*  Description : Rembobine le paquet de données à son départ.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rewind_packed_buffer(packed_buffer_t *pbuf)
{
    pbuf->pos = sizeof(uint32_t);

    assert(pbuf->pos <= pbuf->allocated);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à réinitialiser. [OUT]              *
*                                                                             *
*  Description : Réinitialise un paquet réseau pour une constitution.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_packed_buffer(packed_buffer_t *pbuf)
{
    pbuf->used = 0;

    rewind_packed_buffer(pbuf);

    assert(pbuf->pos <= pbuf->allocated);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à libérer.                          *
*                                                                             *
*  Description : Efface les données contenues par un paquet réseau.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_packed_buffer(packed_buffer_t *pbuf)
{
#ifndef NDEBUG
    assert(pbuf->data != NULL);
#endif

    if (pbuf->data)
    {
        free(pbuf->data);
        pbuf->data = NULL;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = tampon de données à constituer.                       *
*                src  = tampon de données à copier.                           *
*                                                                             *
*  Description : Copie les données d'un tampon dans un autre.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_packed_buffer(packed_buffer_t *dest, const packed_buffer_t *src)
{
    size_t len;                             /* Taille des données à copier */

    exit_packed_buffer(dest);

    len = dest->allocated * sizeof(uint8_t);

    dest->allocated = src->allocated;
    dest->data = malloc(len);

    memcpy(dest->data, src->data, len);

    dest->used = src->used;
    dest->pos = src->pos;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = tampon de données à constituer.                       *
*                src  = tampon de données à copier.                           *
*                                                                             *
*  Description : Inclut les données d'un tampon dans un autre.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool include_packed_buffer(packed_buffer_t *dest, const packed_buffer_t *src)
{
    bool result;                            /* Bilan à retourner           */

    assert(src->allocated >= (sizeof(uint32_t) + src->used));

    result = extend_packed_buffer(dest, src->data + sizeof(uint32_t), src->used, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à consulter.                        *
*                                                                             *
*  Description : Indique le nombre d'octets de la charge utile d'un paquet.   *
*                                                                             *
*  Retour      : Quantité de données utiles.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t get_packed_buffer_payload_length(const packed_buffer_t *pbuf)
{
    size_t result;                          /* Quantité à renvoyer         */

    result = pbuf->used;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à consulter.                        *
*                                                                             *
*  Description : Détermine si des données sont disponibles en lecture.        *
*                                                                             *
*  Retour      : true si des données peuvent être dépilées, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_more_data_in_packed_buffer(const packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = (pbuf->pos < (pbuf->used + sizeof(uint32_t)));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à compléter.                        *
*                data = nouvelles données à ajouter.                          *
*                len  = quantité de ces données.                              *
*                hton = indique si une conversion est à réaliser.             *
*                                                                             *
*  Description : Ajoute des données à un paquet en amont à un envoi.          *
*                                                                             *
*  Retour      : true.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool extend_packed_buffer(packed_buffer_t *pbuf, const void *data, size_t len, bool hton)
{
    uint16_t tmp16;                         /* Valeur intermédiaire 16b    */
    uint32_t tmp32;                         /* Valeur intermédiaire 32b    */
    uint64_t tmp64;                         /* Valeur intermédiaire 64b    */

    /* Réallocation nécessaire ? */

    while ((pbuf->pos + len) > pbuf->allocated)
    {
        pbuf->allocated += PACKET_BLOCK_SIZE;
        pbuf->data = realloc(pbuf->data, pbuf->allocated * sizeof(uint8_t));
    }

    /* Conversion au formalisme du réseau */

    if (!hton)
        goto skip_conversion;

    switch (len)
    {
        case 1:
            *((uint8_t *)(pbuf->data + pbuf->pos)) = *((uint8_t *)data);
            break;

        case 2:
            tmp16 = htobe16(*(uint16_t *)data);
            *((uint16_t *)(pbuf->data + pbuf->pos)) = tmp16;
            break;

        case 4:
            tmp32 = htobe32(*(uint32_t *)data);
            *((uint32_t *)(pbuf->data + pbuf->pos)) = tmp32;
            break;

        case 8:
            tmp64 = htobe64(*(uint64_t *)data);
            *((uint64_t *)(pbuf->data + pbuf->pos)) = tmp64;
            break;

        default:

 skip_conversion:

            /**
             * Dans ce cas de figure, c'est à l'appelant de s'assurer que la
             * conversion a bien été réalisée.
             */
            assert(!hton);

            memcpy(pbuf->data + pbuf->pos, data, len);
            break;

    }

    pbuf->used += len;
    pbuf->pos += len;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à consulter.                        *
*                buf  = nouvelles données à définir.                          *
*                len  = quantité de ces données.                              *
*                ntoh = indique si une conversion est à réaliser.             *
*                                                                             *
*  Description : Récupère des données depuis un paquet après une réception.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool peek_packed_buffer(packed_buffer_t *pbuf, void *buf, size_t len, bool ntoh)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t tmp16;                         /* Valeur intermédiaire 16b    */
    uint32_t tmp32;                         /* Valeur intermédiaire 32b    */
    uint64_t tmp64;                         /* Valeur intermédiaire 64b    */

    result = ((pbuf->pos + len - sizeof(uint32_t)) <= pbuf->used);

    if (!result)
        goto failed;

    /* Conversion au formalisme du réseau */

    if (!ntoh)
        goto skip_conversion;

    switch (len)
    {
        case 1:
            *((uint8_t *)buf) = *((uint8_t *)(pbuf->data + pbuf->pos));
            break;

        case 2:
            tmp16 = be16toh(*(uint16_t *)(pbuf->data + pbuf->pos));
            *((uint16_t *)buf) = tmp16;
            break;

        case 4:
            tmp32 = be32toh(*(uint32_t *)(pbuf->data + pbuf->pos));
            *((uint32_t *)buf) = tmp32;
            break;

        case 8:
            tmp64 = be64toh(*(uint64_t *)(pbuf->data + pbuf->pos));
            *((uint64_t *)buf) = tmp64;
            break;

        default:

 skip_conversion:

            /**
             * Dans ce cas de figure, c'est à l'appelant de s'assurer que la
             * conversion a bien été réalisée.
             */
            assert(!ntoh);

            memcpy(buf, pbuf->data + pbuf->pos, len);
            break;

    }

 failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à consulter.                        *
*                len  = quantité de ces données.                              *
*                                                                             *
*  Description : Avance la tête de lecture dans les données d'un paquet.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void advance_packed_buffer(packed_buffer_t *pbuf, size_t len)
{
    pbuf->pos += len;

    assert((pbuf->pos - sizeof(uint32_t)) <= pbuf->used);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à consulter.                        *
*                buf  = nouvelles données à définir.                          *
*                len  = quantité de ces données.                              *
*                ntoh = indique si une conversion est à réaliser.             *
*                                                                             *
*  Description : Récupère des données depuis un paquet après une réception.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool extract_packed_buffer(packed_buffer_t *pbuf, void *buf, size_t len, bool ntoh)
{
    bool result;                            /* Bilan à retourner           */

    result = peek_packed_buffer(pbuf, buf, len, ntoh);

    if (result)
        advance_packed_buffer(pbuf, len);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à constituer. [OUT]                 *
*                fd   = flux ouvert en lecture.                               *
*                                                                             *
*  Description : Lit des données depuis un flux local.                        *
*                                                                             *
*  Retour      : true si toutes les données ont été reçues, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_packed_buffer(packed_buffer_t *pbuf, int fd)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t used;                          /* Taille de charge utile      */

    result = safe_read(fd, &used, sizeof(uint32_t));

    if (result)
    {
        assert(pbuf->pos == sizeof(uint32_t));

        if ((pbuf->pos + used) > pbuf->allocated)
        {
            pbuf->allocated = pbuf->pos + used;
            pbuf->data = realloc(pbuf->data, pbuf->allocated * sizeof(uint8_t));
        }

        pbuf->used = used;

        result = safe_read(fd, pbuf->data + pbuf->pos, used);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à émettre.                          *
*                fd   = flux ouvert en écriture.                              *
*                                                                             *
*  Description : Ecrit des données dans un flux local.                        *
*                                                                             *
*  Retour      : true si toutes les données ont été émises, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_packed_buffer(packed_buffer_t *pbuf, int fd)
{
    bool result;                            /* Bilan à retourner           */

    *((uint32_t *)pbuf->data) = pbuf->used;

    result = safe_write(fd, pbuf->data, sizeof(uint32_t) + pbuf->used);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à constituer. [OUT]                 *
*                fd   = flux ouvert en lecture.                               *
*                                                                             *
*  Description : Réceptionne des données depuis un flux réseau.               *
*                                                                             *
*  Retour      : true si toutes les données ont été reçues, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool recv_packed_buffer(packed_buffer_t *pbuf, int fd)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t used;                          /* Taille de charge utile      */

    result = safe_recv(fd, &used, sizeof(uint32_t), 0);

    if (result)
    {
        assert(pbuf->pos == sizeof(uint32_t));

        if ((pbuf->pos + used) > pbuf->allocated)
        {
            pbuf->allocated = pbuf->pos + used;
            pbuf->data = realloc(pbuf->data, pbuf->allocated * sizeof(uint8_t));
        }

        pbuf->used = used;

        result = safe_recv(fd, pbuf->data + pbuf->pos, used, 0);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à émettre.                          *
*                fd   = flux ouvert en écriture.                              *
*                                                                             *
*  Description : Envoie des données au travers un flux réseau.                *
*                                                                             *
*  Retour      : true si toutes les données ont été émises, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool send_packed_buffer(packed_buffer_t *pbuf, int fd)
{
    bool result;                            /* Bilan à retourner           */

    *((uint32_t *)pbuf->data) = pbuf->used;

    result = safe_send(fd, pbuf->data, sizeof(uint32_t) + pbuf->used, 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à constituer. [OUT]                 *
*                fd   = flux ouvert en lecture.                               *
*                                                                             *
*  Description : Réceptionne des données depuis un flux réseau chiffré.       *
*                                                                             *
*  Retour      : true si toutes les données ont été reçues, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ssl_recv_packed_buffer(packed_buffer_t *pbuf, SSL *fd)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t used;                          /* Taille de charge utile      */
    size_t pos;                             /* Localisation du stockage    */
    size_t remaining;                       /* Quantité à lire restante    */
    size_t got;                             /* QUantité lue par appel      */
    int ret;                                /* Code de retour d'une lecture*/

    got = SSL_read(fd, &used, sizeof(uint32_t));
    if (got <= 0) LOG_ERROR_OPENSSL;

    result = (got == sizeof(uint32_t));

    if (result)
    {
        assert(pbuf->pos == sizeof(uint32_t));

        if ((pbuf->pos + used) > pbuf->allocated)
        {
            pbuf->allocated = pbuf->pos + used;
            pbuf->data = realloc(pbuf->data, pbuf->allocated * sizeof(uint8_t));
        }

        pbuf->used = used;

        pos = pbuf->pos;
        remaining = used;

        while (remaining > 0)
        {
            ret = SSL_read_ex(fd, pbuf->data + pos, remaining, &got);

            if (ret > 0)
            {
                pos += got;
                remaining -= got;
            }

            else
            {
                LOG_ERROR_OPENSSL;
                break;
            }

        }

        result = (remaining == 0);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = paquet de données à émettre.                          *
*                fd   = flux ouvert en écriture.                              *
*                                                                             *
*  Description : Envoie des données au travers un flux réseau chiffré.        *
*                                                                             *
*  Retour      : true si toutes les données ont été émises, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ssl_send_packed_buffer(packed_buffer_t *pbuf, SSL *fd)
{
    bool result;                            /* Bilan à retourner           */
    int quantity;                           /* Nombre de données à traiter */
    int sent;                               /* Quantité de données traitées*/

    *((uint32_t *)pbuf->data) = pbuf->used;

    quantity = sizeof(uint32_t) + pbuf->used;

    sent = SSL_write(fd, pbuf->data, quantity);
    if (sent <= 0) LOG_ERROR_OPENSSL;

    result = (quantity == sent);

    return result;

}
