
/* Chrysalide - Outil d'analyse de fichiers binaires
 * simple.c - décodage de simples chaînes de caractères Dex
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "simple.h"


#include <malloc.h>
#include <string.h>


#include <common/utf8.h>



/* Extrait un simple caractère depuis un codage Dex. */
static size_t dcd_simple_name_char(input_buffer *);



/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                                                                             *
*  Description : Extrait une simple chaîne de caractères depuis un codage Dex.*
*                                                                             *
*  Retour      : Chaîne MUTF-8 terminée par un octet nul ou NULL si erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *dcd_simple_name(input_buffer *buffer)
{
    char *result;                           /* Nom extrait à renvoyer      */
    const char *start;                      /* Conservation du départ      */
    size_t count;                           /* Taille du nom constitué     */
    size_t extra;                           /* Taille de nouveau caractère */

    /**
     * La règle traitée est la suivante :
     *
     *    SimpleName →
     *        SimpleNameChar (SimpleNameChar)*
     *
     */

    start = get_input_buffer_text_access(buffer);

    count = 0;

    do
    {
        extra = dcd_simple_name_char(buffer);
        count += extra;
    }
    while (extra > 0);

    if (count == 0)
        result = NULL;

    else
    {
        result = malloc((count + 1) * sizeof(char));

        memcpy(result, start, count);
        result[count] = '\0';

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les données utiles.                *
*                                                                             *
*  Description : Extrait un simple caractère depuis un codage Dex.            *
*                                                                             *
*  Retour      : quantité de données consommées, 0 en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t dcd_simple_name_char(input_buffer *buffer)
{
    size_t result;                          /* Avancée à retourner         */
    const char *text;                       /* Accès au texte à relire     */
    size_t remaining;                       /* Quantité restante           */
    unichar_t wc;                           /* Caractère étendu lu         */

    /**
     * La règle traitée est la suivante :
     *
     *    SimpleNameChar →
     *        'A' … 'Z'
     *    |   'a' … 'z'
     *    |   '0' … '9'
     *    |   '$'
     *    |   '-'
     *    |   '_'
     *    |   U+00a1 … U+1fff
     *    |   U+2010 … U+2027
     *    |   U+2030 … U+d7ff
     *    |   U+e000 … U+ffef
     *    |   U+10000 … U+10ffff
     *
     */

    text = get_input_buffer_text_access(buffer);
    remaining = count_input_buffer_remaining(buffer);

    wc = decode_mutf8_char((unsigned char *)text, remaining, &result);

    if (IS_UTF8_ERROR(wc))
        return 0;

    switch (wc)
    {
        case 'A' ... 'Z':
        case 'a' ... 'z':
        case '0' ... '9':
        case '$':
        case '-':
        case '_':
        case 0x00a1 ... 0x1fff:
        case 0x2010 ... 0x2027:
        case 0x2030 ... 0xd7ff:
        case 0xe000 ... 0xffef:
        case 0x10000 ... 0x10ffff:
            advance_input_buffer(buffer, result);
            break;

        default:
            result = 0;

    }

    return result;

}
