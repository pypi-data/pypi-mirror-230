
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ibuf.h - prototypes pour la lecture progressive d'un tampon de données
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _COMMON_IBUF_H
#define _COMMON_IBUF_H


#include <stdbool.h>
#include <stdint.h>
#include <sys/types.h>



/* Rassemblement de données d'un tampon */
typedef struct _input_buffer
{
    union
    {
        const char *text;                   /* Contenu textuel disponible  */
        const uint8_t *data;                /* Données brutes à traiter    */
    };

    size_t len;                             /* Quantité d'octets présents  */
    size_t pos;                             /* Position de tête de lecture */

} input_buffer;


/* Initialise un contenu textuel pour une lecture ultérieure. */
void init_text_input_buffer(input_buffer *, const char *);

/* Fournit la taille totale du tampon constitué. */
size_t get_input_buffer_size(const input_buffer *);

/* Compte le nombre d'octets encore non lus. */
size_t count_input_buffer_remaining(const input_buffer *);

/* Détermine s'il reste encore des données disponibles. */
bool input_buffer_contain_data(const input_buffer *);

/* Avance la tête de lecture dans le tampon de données. */
void advance_input_buffer(input_buffer *, size_t);

/* Fournit un accès brut au niveau de la tête de lecture. */
const char *get_input_buffer_text_access(const input_buffer *);

/* Fournit la chaîne de caractère restant à traiter. */
const char *get_input_buffer_string(const input_buffer *, size_t *);

/* Fournit le caractère courant à la tête de lecture courante. */
char peek_input_buffer_char(const input_buffer *);

/* Fournit le caractère suivant la tête de lecture courante. */
char peek_input_buffer_next_char(const input_buffer *);

/* Fournit et avance la tête de lecture courante. */
char get_input_buffer_next_char(input_buffer *);

/* Fournit et avance la tête de lecture courante, si possible. */
bool get_input_buffer_next_char_carefully(input_buffer *, char *);

/* Vérifie la nature du caractère courant. */
bool check_input_buffer_char(input_buffer *, char);

/* Note la position courante de la tête de lecture. */
void save_input_buffer_pos(const input_buffer *, size_t *);

/* Restaure la position de la tête de lecture. */
void restore_input_buffer_pos(input_buffer *, size_t);



#endif  /* _COMMON_IBUF_H */
