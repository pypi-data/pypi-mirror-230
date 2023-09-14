
/* Chrysalide - Outil d'analyse de fichiers binaires
 * utils.h - fonctions qui simplifient la vie dans les interactions avec un serveur GDB
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


#include "utils.h"


#include <assert.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdbool.h>
#include <sys/param.h>
#include <sys/types.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : data = données à inspecter.                                  *
*                len  = quantité de ces données.                              *
*                                                                             *
*  Description : Indique si les données correspondent à un code d'erreur.     *
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_error_code(const char *data, size_t len)
{
    bool result;                            /* Bilan à retourner           */

    result = (len == 3);

    if (result)
        result = (data[0] == 'E' && isdigit(data[1]) && isdigit(data[2]));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = données à analyser.                                   *
*                size = taille de ces données.                                *
*                byte = statut de sortie d'un programme. [OUT]                *
*                                                                             *
*  Description : Relit une valeur sur 8 bits et deux lettres.                 *
*                                                                             *
*  Retour      : Bilan de la lecture.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_fixed_byte(const char *data, size_t len, uint8_t *byte)
{
    bool result;                            /* Bilan à retourner           */
    const char *iter;                       /* Boucle de parcours #1       */
    size_t i;                               /* Boucle de parcours #2       */
    uint8_t nibble;                         /* Valeur affichée             */

    result = true;

    len = MIN(2, len);

    for (i = 0, iter = data; i < len; i++, iter++)
    {
        switch (*iter)
        {
            case '0' ... '9':
                nibble = *iter - '0';
                break;

            case 'a' ... 'f':
                nibble = *iter - 'a' + 10;
                break;

            case 'A' ... 'F':
                nibble = *iter - 'A' + 10;
                break;

            default:
                result = false;
                break;

        }

        if (!result)
            break;

        if (i == 0)
            *byte = (nibble << 4);
        else
            *byte |= nibble;

    }

    if (result)
        result = (i == 2);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hex   = tampon d'origine assez grand.                        *
*                size  = taille de la valeur à considérer pour les travaux.   *
*                value = valeur sur XX bits à transcrire. [OUT]               *
*                                                                             *
*  Description : Traduit en valeur sur XX bits une forme textuelle.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool hex_to_any_u(const char *hex, size_t size, ...)
{
    bool result;                            /* Bilan à retourner           */
    va_list ap;                             /* Gestion de l'inconnue       */
    uint8_t *value8;                        /* Valeur sur 8 bits           */
    uint16_t *value16;                      /* Valeur sur 16 bits          */
    uint32_t *value32;                      /* Valeur sur 32 bits          */
    uint64_t *value64;                      /* Valeur sur 64 bits          */
    uint8_t *iter;                          /* Boucle de parcours #1       */
    size_t i;                               /* Boucle de parcours #2       */
    char nibble;                            /* Valeur à afficher           */

    result = false;

    /* Récupération de la destination */

    va_start(ap, size);

    switch (size)
    {
        case 1:
            value8 = va_arg(ap, uint8_t *);
            iter = value8;
            break;

        case 2:
            value16 = va_arg(ap, uint16_t *);
            iter = (uint8_t *)value16;
            break;

        case 4:
            value32 = va_arg(ap, uint32_t *);
            iter = (uint8_t *)value32;
            break;

        case 8:
            value64 = va_arg(ap, uint64_t *);
            iter = (uint8_t *)value64;
            break;

        default:
            goto done;
            break;

    }

    /* Lecture de la valeur */

    for (i = 0; i < size; i++, iter++)
    {
        *iter = 0;

        nibble = hex[i * 2];

        switch (nibble)
        {
            case '0' ... '9':
                *iter = (nibble - '0') << 4;
                break;

            case 'a' ... 'f':
                *iter = (nibble - 'a' + 0xa) << 4;
                break;

            case 'A' ... 'F':
                *iter = (nibble - 'A' + 0xa) << 4;
                break;

            default:
                goto done;
                break;

        }

        nibble = hex[i * 2 + 1];

        switch (nibble)
        {
            case '0' ... '9':
                *iter |= (nibble - '0');
                break;

            case 'a' ... 'f':
                *iter |= (nibble - 'a' + 0xa);
                break;

            case 'A' ... 'F':
                *iter |= (nibble - 'A' + 0xa);
                break;

            default:
                goto done;
                break;

        }

    }

    result = (i == size);

 done:

    va_end(ap);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : size  = taille de la valeur à considérer pour les travaux.   *
*                hex   = tampon de destination assez grand.                   *
*                value = valeur sur XX bits à transcrire. [OUT]               *
*                                                                             *
*  Description : Traduit une valeur sur XX bits en forme textuelle.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool any_u_to_hex(size_t size, char hex[17], ...)
{
    bool result;                            /* Bilan à retourner           */
    va_list ap;                             /* Gestion de l'inconnue       */
    uint8_t *value8;                        /* Valeur sur 8 bits           */
    uint16_t *value16;                      /* Valeur sur 16 bits          */
    uint32_t *value32;                      /* Valeur sur 32 bits          */
    uint64_t *value64;                      /* Valeur sur 64 bits          */
    size_t i;                               /* Boucle de parcours #1       */
    const uint8_t *iter;                    /* Boucle de parcours #2       */
    uint8_t nibble;                         /* Valeur à retenir            */

    result = true;

    /* Récupération de la destination */

    va_start(ap, hex);

    switch (size)
    {
        case 1:
            value8 = va_arg(ap, uint8_t *);
            iter = (const uint8_t *)value8;
            break;

        case 2:
            value16 = va_arg(ap, uint16_t *);
            iter = (const uint8_t *)value16;
            break;

        case 4:
            value32 = va_arg(ap, uint32_t *);
            iter = (const uint8_t *)value32;
            break;

        case 8:
            value64 = va_arg(ap, uint64_t *);
            iter = (const uint8_t *)value64;
            break;

        default:
            result = false;
            goto done;
            break;

    }

    /* Lecture de la valeur */

    for (i = 0; i < size; i++, iter++)
    {
        nibble = (*iter & 0xf0) >> 4;

        switch (nibble)
        {
            case 0x0 ... 0x9:
                hex[i * 2] = '0' + nibble;
                break;

            case 0xa ... 0xf:
                hex[i * 2] = 'A' + nibble - 0xa;
                break;

        }

        nibble = (*iter & 0x0f);

        switch (nibble)
        {
            case 0x0 ... 0x9:
                hex[i * 2 + 1] = '0' + nibble;
                break;

            case 0xa ... 0xf:
                hex[i * 2 + 1] = 'A' + nibble - 0xa;
                break;

        }

    }

    hex[size * 2] = '\0';

 done:

    va_end(ap);

    return result;

}
