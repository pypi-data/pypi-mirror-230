
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packed.h - prototypes pour le regroupement de bribes de paquets réseau
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


#ifndef _COMMON_PACKED_H
#define _COMMON_PACKED_H


#include <stdbool.h>
#include <stdint.h>
#include <openssl/ssl.h>
#include <sys/types.h>


#include "io.h"



/* Rassemblement de données d'un paquet */
typedef struct _packed_buffer_t
{
    uint8_t *data;                          /* Données à traiter           */
    size_t allocated;                       /* Taille allouée              */

    size_t used;                            /* Quantité de données utiles  */
    size_t pos;                             /* Tête de lecture/écriture    */

} packed_buffer_t;


/* Initialise un paquet réseau pour une constitution. */
void init_packed_buffer(packed_buffer_t *);

/* Rembobine le paquet de données à son départ. */
void rewind_packed_buffer(packed_buffer_t *);

/* Réinitialise un paquet réseau pour une constitution. */
void reset_packed_buffer(packed_buffer_t *);

/* Efface les données contenues par un paquet réseau. */
void exit_packed_buffer(packed_buffer_t *);

/* Copie les données d'un tampon dans un autre. */
void copy_packed_buffer(packed_buffer_t *, const packed_buffer_t *);

/* Inclut les données d'un tampon dans un autre. */
bool include_packed_buffer(packed_buffer_t *, const packed_buffer_t *);

/* Indique le nombre d'octets de la charge utile d'un paquet. */
size_t get_packed_buffer_payload_length(const packed_buffer_t *);

/* Détermine si des données sont disponibles en lecture. */
bool has_more_data_in_packed_buffer(const packed_buffer_t *);

/* Ajoute des données à un paquet en amont à un envoi. */
bool extend_packed_buffer(packed_buffer_t *, const void *, size_t, bool);

/* Récupère des données depuis un paquet après une réception. */
bool peek_packed_buffer(packed_buffer_t *, void *, size_t, bool);

/* Avance la tête de lecture dans les données d'un paquet. */
void advance_packed_buffer(packed_buffer_t *, size_t);

/* Récupère des données depuis un paquet après une réception. */
bool extract_packed_buffer(packed_buffer_t *, void *, size_t, bool);

/* Lit des données depuis un flux local. */
bool read_packed_buffer(packed_buffer_t *, int);

/* Ecrit des données dans un flux local. */
bool write_packed_buffer(packed_buffer_t *, int);

/* Réceptionne des données depuis un flux réseau. */
bool recv_packed_buffer(packed_buffer_t *, int);

/* Envoie des données au travers un flux réseau. */
bool send_packed_buffer(packed_buffer_t *, int);

/* Réceptionne des données depuis un flux réseau chiffré. */
bool ssl_recv_packed_buffer(packed_buffer_t *, SSL *);

/* Envoie des données au travers un flux réseau chiffré. */
bool ssl_send_packed_buffer(packed_buffer_t *, SSL *);



#endif  /* _COMMON_PACKED_H */
