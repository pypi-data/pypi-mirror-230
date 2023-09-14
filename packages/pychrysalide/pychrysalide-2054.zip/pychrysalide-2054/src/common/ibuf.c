
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ibuf.c - lecture progressive d'un tampon de données
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


#include "ibuf.h"


#include <assert.h>
#include <string.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à initialiser. [OUT]                *
*                                                                             *
*  Description : Initialise un contenu textuel pour une lecture ultérieure.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_text_input_buffer(input_buffer *ibuf, const char *text)
{
    ibuf->text = text;

    ibuf->len = strlen(text);
    ibuf->pos = 0;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                                                                             *
*  Description : Fournit la taille totale du tampon constitué.                *
*                                                                             *
*  Retour      : Valeur positive (ou nulle !).                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t get_input_buffer_size(const input_buffer *ibuf)
{
    size_t result;                          /* Quantité à retourner        */

    result = ibuf->len;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                                                                             *
*  Description : Compte le nombre d'octets encore non lus.                    *
*                                                                             *
*  Retour      : Nombre d'octets encore disponibles pour un traitement.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t count_input_buffer_remaining(const input_buffer *ibuf)
{
    size_t result;                          /* Quantité à renvoyer         */

    assert(ibuf->pos <= (ibuf->len + 1));

    if (ibuf->pos > ibuf->len)
        result = 0;

    else
        result = ibuf->len - ibuf->pos;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                                                                             *
*  Description : Détermine s'il reste encore des données disponibles.         *
*                                                                             *
*  Retour      : true si des données sont encore présentes, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool input_buffer_contain_data(const input_buffer *ibuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t remaining;                       /* Quantité restante           */

    remaining = count_input_buffer_remaining(ibuf);

    result = (remaining > 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf  = tampon de données à modifier.                        *
*                count = progression de la tête de lecture à marquer.         *
*                                                                             *
*  Description : Avance la tête de lecture dans le tampon de données.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void advance_input_buffer(input_buffer *ibuf, size_t count)
{
    assert((ibuf->pos + count) <= (ibuf->len + 1));

    ibuf->pos += count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                                                                             *
*  Description : Fournit un accès brut au niveau de la tête de lecture.       *
*                                                                             *
*  Retour      : Référence au texte brut courant.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_input_buffer_text_access(const input_buffer *ibuf)
{
    return ibuf->text + ibuf->pos;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                remaining = taille de la chaîne retournée. [OUT]             *
*                                                                             *
*  Description : Fournit la chaîne de caractère restant à traiter.            *
*                                                                             *
*  Retour      : Pointeur vers les données courantes.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_input_buffer_string(const input_buffer *ibuf, size_t *remaining)
{
    const char *result;                     /* Pointeur à retourner        */

    assert(ibuf->pos <= ibuf->len);

    result = ibuf->text + ibuf->pos;

    *remaining = ibuf->len - ibuf->pos;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à parcourir.                        *
*                                                                             *
*  Description : Fournit le caractère courant à la tête de lecture courante.  *
*                                                                             *
*  Retour      : Caractère courant.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char peek_input_buffer_char(const input_buffer *ibuf)
{
    assert(ibuf->pos <= ibuf->len);

    return *(ibuf->text + ibuf->pos);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à parcourir.                        *
*                                                                             *
*  Description : Fournit le caractère suivant la tête de lecture courante.    *
*                                                                             *
*  Retour      : Caractère courant.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char peek_input_buffer_next_char(const input_buffer *ibuf)
{
    char result;                            /* Valeur à retourner          */

    assert(ibuf->pos <= ibuf->len);

    if (ibuf->pos == ibuf->len)
        result = '\0';

    else
        result = *(ibuf->text + ibuf->pos + 1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à parcourir.                        *
*                                                                             *
*  Description : Fournit et avance la tête de lecture courante.               *
*                                                                             *
*  Retour      : Caractère courant.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char get_input_buffer_next_char(input_buffer *ibuf)
{
    char result;                            /* Valeur à retourner          */

    assert(ibuf->pos <= ibuf->len);

    result = *(ibuf->text + ibuf->pos);

    advance_input_buffer(ibuf, 1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à parcourir.                        *
*                out  = caractère courant, s'il existe.                       *
*                                                                             *
*  Description : Fournit et avance la tête de lecture courante, si possible.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_input_buffer_next_char_carefully(input_buffer *ibuf, char *out)
{
    char result;                            /* Valeur à retourner          */

    assert(ibuf->pos <= ibuf->len);

    result = input_buffer_contain_data(ibuf);

    if (result)
    {
        *out = *(ibuf->text + ibuf->pos);

        advance_input_buffer(ibuf, 1);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à parcourir.                        *
*                c    = caractère à retrouver.                                *
*                                                                             *
*  Description : Vérifie la nature du caractère courant.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_input_buffer_char(input_buffer *ibuf, char c)
{
    bool result;                            /* Validation à retourner      */

    if (peek_input_buffer_char(ibuf) == c)
    {
        result = true;
        advance_input_buffer(ibuf, 1);
    }
    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                pos  = sauvegarde de la tête de lecture. [OUT]               *
*                                                                             *
*  Description : Note la position courante de la tête de lecture.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void save_input_buffer_pos(const input_buffer *ibuf, size_t *pos)
{
    *pos = ibuf->pos;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ibuf = tampon de données à consulter.                        *
*                pos  = tête de lecture à définir pour le tampon courant.     *
*                                                                             *
*  Description : Restaure la position de la tête de lecture.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void restore_input_buffer_pos(input_buffer *ibuf, size_t pos)
{
    assert(pos <= ibuf->len);

    ibuf->pos = pos;

}
