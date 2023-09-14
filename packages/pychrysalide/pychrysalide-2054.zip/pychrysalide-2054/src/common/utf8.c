
/* Chrysalide - Outil d'analyse de fichiers binaires
 * utf8.c - support minimaliste mais adapté de l'encodage UTF-8
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


#include "utf8.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : text     = position courante dans une chaîne de caractères.  *
*                len      = nombre d'octets de cette même chaîne.             *
*                consumed = nombre d'octets lus pendant l'opération. [OUT]    *
*                                                                             *
*  Description : Procède à la lecture d'un caractère dans une chaîne en UTF-8.*
*                                                                             *
*  Retour      : Caractère sur 32 bits lu ou code d'erreur en cas de soucis.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unichar_t decode_utf8_char(const unsigned char *text, size_t len, size_t *consumed)
{
    unichar_t result;                       /* Valeur à retourner          */
    size_t expected;                        /* Quantité à traiter          */
    unichar_t minval;                       /* Valeur codée minimale       */
    size_t i;                               /* Boucle de parcours          */

    result = text[0];

    /**
     * ASCII ?
     */
    if (result < 0x80)
    {
        *consumed = 1;
        goto duc_done;
    }

    /**
     * Deux caractères (au moins) doivent être présents.
     * Le premier mot doit donc au moins commencer par 0b1100 = 0xc.
     */
    else if (result < 0xc0)
    {
        result = UTF8_ERROR_MALFORMED;
        goto duc_done;
    }

    /**
     * Valeur inférieure à 0xe, donc taille inférieure à 3 (0b1110).
     */
    else if (result < 0xe0)
    {
        expected = 2;
        result &= 0x1f;
        minval = 1 << 7;
    }

    /**
     * Valeur inférieure à 0xf0, donc taille inférieure à 4 (0b11110000).
     */
    else if (result < 0xf0)
    {
        expected = 3;
        result &= 0x0f;
        minval = 1 << 11;
    }

    /**
     * Valeur inférieure à 0xf8, donc taille inférieure à 5 (0b11111000).
     */
    else if (result < 0xf8)
    {
        expected = 4;
        result &= 0x07;
        minval = 1 << 16;
    }

    /**
     * Erreur : l'encodage UTF-8 ne dépasse pas 4 octets.
     */
    else
    {
        result = UTF8_ERROR_TOO_LONG;
        goto duc_done;
    }

    /**
     * Erreur : pas assez de données.
     */
    if (expected > len)
    {
        result = UTF8_ERROR_TOO_LONG;
        goto duc_done;
    }

    /**
     * Intégration des octets restants, avec vérifications qu'ils participent
     * bien à la constitution de la valeur finale.
     */
    for (i = 1; i < expected; i++)
    {
        if ((text[i] & 0xc0) != 0x80)
        {
            result = UTF8_ERROR_MISSING;
            goto duc_done;
        }

        result <<= 6;
        result |= (text[i] & 0x3f);

    }

    /**
     * Validation finale.
     */
    if (result < minval)
    {
        result = UTF8_ERROR_WASTING;
        goto duc_done;
    }

    *consumed = expected;

 duc_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : text     = position courante dans une chaîne de caractères.  *
*                len      = nombre d'octets de cette même chaîne.             *
*                consumed = nombre d'octets lus pendant l'opération. [OUT]    *
*                                                                             *
*  Description : Procède à la lecture d'un caractère d'une chaîne en MUTF-8.  *
*                                                                             *
*  Retour      : Caractère sur 32 bits lu ou code d'erreur en cas de soucis.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unichar_t decode_mutf8_char(const unsigned char *text, size_t len, size_t *consumed)
{
    unichar_t result;                       /* Valeur à retourner          */
    size_t expected;                        /* Quantité à traiter          */
    unichar_t minval;                       /* Valeur codée minimale       */
    size_t i;                               /* Boucle de parcours          */

    /**
     * Le format suivant est détaillé à la page :
     * https://source.android.com/devices/tech/dalvik/dex-format#mutf-8
     */

    result = text[0];

    /**
     * ASCII ?
     */
    if (result < 0x80)
    {
        *consumed = 1;
        goto duc_done;
    }

    /**
     * Deux caractères (au moins) doivent être présents.
     * Le premier mot doit donc au moins commencer par 0b1100 = 0xc.
     */
    else if (result < 0xc0)
    {
        result = UTF8_ERROR_MALFORMED;
        goto duc_done;
    }

    /**
     * Valeur inférieure à 0xe, donc taille inférieure à 3 (0b1110).
     */
    else if (result < 0xe0)
    {
        expected = 2;
        result &= 0x1f;
        minval = 1 << 7;
    }

    /**
     * Valeur inférieure à 0xf0, donc taille inférieure à 4 (0b11110000).
     */
    else if (result < 0xf0)
    {
        expected = 3;
        result &= 0x0f;
        minval = 1 << 11;
    }

    /**
     * Erreur : l'encodage MUTF-8 ne dépasse pas 3 octets.
     */
    else
    {
        result = UTF8_ERROR_TOO_LONG;
        goto duc_done;
    }

    /**
     * Erreur : pas assez de données.
     */
    if (expected > len)
    {
        result = UTF8_ERROR_TOO_LONG;
        goto duc_done;
    }

    /**
     * Intégration des octets restants, avec vérifications qu'ils participent
     * bien à la constitution de la valeur finale.
     */
    for (i = 1; i < expected; i++)
    {
        if ((text[i] & 0xc0) != 0x80)
        {
            result = UTF8_ERROR_MISSING;
            goto duc_done;
        }

        result <<= 6;
        result |= (text[i] & 0x3f);

    }

    /**
     * Validation finale.
     */
    if (result < minval && (result != 0 || expected != 2))
    {
        result = UTF8_ERROR_WASTING;
        goto duc_done;
    }

    *consumed = expected;

 duc_done:

    return result;

}
