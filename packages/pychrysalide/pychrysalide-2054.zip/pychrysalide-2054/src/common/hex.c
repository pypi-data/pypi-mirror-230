
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.c - construction et interprétation de chaînes hexadécimales
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "hex.h"


#include <ctype.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : src   = source de données à considérer.                      *
*                len   = quantité de ces données à traiter.                   *
*                lower = spécifie un encodage à l'aide de minuscules.         *
*                dst   = zone allouée pour les données résultantes. [OUT]     *
*                                                                             *
*  Description : Encode des données en chaîne hexadécimale.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void encode_hex(const char *src, size_t len, bool lower, char *dst)
{
    size_t i;                               /* Boucle de parcours #1       */
    uint8_t index;                          /* Indice de recherche         */

    /**
     * base = "".join([ "%02X" % i for i in range(256) ])
     * encoded = "\n".join([ base[i : i + 32] for i in range(0, 512, 32) ])
     * print(encoded)
     */
    const char encoding_lookup[] = {
        "000102030405060708090A0B0C0D0E0F"
        "101112131415161718191A1B1C1D1E1F"
        "202122232425262728292A2B2C2D2E2F"
        "303132333435363738393A3B3C3D3E3F"
        "404142434445464748494A4B4C4D4E4F"
        "505152535455565758595A5B5C5D5E5F"
        "606162636465666768696A6B6C6D6E6F"
        "707172737475767778797A7B7C7D7E7F"
        "808182838485868788898A8B8C8D8E8F"
        "909192939495969798999A9B9C9D9E9F"
        "A0A1A2A3A4A5A6A7A8A9AAABACADAEAF"
        "B0B1B2B3B4B5B6B7B8B9BABBBCBDBEBF"
        "C0C1C2C3C4C5C6C7C8C9CACBCCCDCECF"
        "D0D1D2D3D4D5D6D7D8D9DADBDCDDDEDF"
        "E0E1E2E3E4E5E6E7E8E9EAEBECEDEEEF"
        "F0F1F2F3F4F5F6F7F8F9FAFBFCFDFEFF"
    };

    for (i = 0; i < len; i++)
    {
        index = src[i];

        if (lower)
        {
            (*dst++) = tolower(encoding_lookup[index * 2]);
            (*dst++) = tolower(encoding_lookup[index * 2 + 1]);
        }
        else
        {
            (*dst++) = encoding_lookup[index * 2];
            (*dst++) = encoding_lookup[index * 2 + 1];
        }

    }

    *dst = '\0';

}


/******************************************************************************
*                                                                             *
*  Paramètres  : digit = caractère hexadécimale à transcrire.                 *
*                value = valeur récupérée. [OUT]                              *
*                                                                             *
*  Description : Décode un caractère hexadécimal.                             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool decode_hex_digit(const char *digit, uint8_t *value)
{
    bool result;                            /* Validité à retourner        */

    switch (*digit)
    {
        case '0' ... '9':
            *value = (*digit) - '0';
            result = true;
            break;

        case 'a' ... 'f':
            *value = 0xa + (*digit) - 'a';
            result = true;
            break;

        case 'A' ... 'F':
            *value = 0xa + (*digit) - 'A';
            result = true;
            break;

        default:
            result = false;
            break;

    }

    return result;

}
