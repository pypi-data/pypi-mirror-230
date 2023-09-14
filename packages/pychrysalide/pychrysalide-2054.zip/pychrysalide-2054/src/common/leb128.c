
/* Chrysalide - Outil d'analyse de fichiers binaires
 * leb128.c - support des valeurs encodées au format LEB128.
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "leb128.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                len    = taille totale des données à analyser.               *
*                                                                             *
*  Description : Lit un nombre non signé encodé au format LEB128.             *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_uleb128(uleb128_t *target, const bin_t *data, phys_t *pos, phys_t len)
{
    int shift;                              /* Décalage à appliquer        */
    phys_t i;                               /* Boucle de parcours          */

    shift = 0;
    *target = 0;

    for (i = 0; i < 8; i++)
    {
        /* On évite les débordements... */
        if (*pos >= len) return false;

        *target |= (data[*pos] & 0x7f) << shift;

        shift += 7;
        (*pos)++;

        if ((data[*pos - 1] & 0x80) == 0x00) break;

    }

    return (i < 8);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                len    = taille totale des données à analyser.               *
*                                                                             *
*  Description : Lit un nombre signé encodé au format LEB128.                 *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_leb128(leb128_t *target, const bin_t *data, phys_t *pos, phys_t len)
{
    int shift;                              /* Décalage à appliquer        */
    phys_t i;                               /* Boucle de parcours          */

    shift = 0;
    *target = 0;

    for (i = 0; i < 8; i++)
    {
        /* On évite les débordements... */
        if (*pos >= len) return false;

        *target |= (data[*pos] & 0x7f) << shift;

        shift += 7;

        if ((data[(*pos)++] & 0x80) == 0x00) break;

    }

    if (shift < (8 * sizeof(int64_t)) && (data[*pos - 1] & 0x40) == 0x40)
        *target |= - (1 << shift);

    return (i < 8);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur à consigner.                                  *
*                pbuf  = tampon de données à constituer. [OUT]                *
*                                                                             *
*  Description : Encode un nombre non signé encodé au format LEB128.          *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_uleb128(const uleb128_t *value, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t tmp;                          /* Valeur modifiable           */
    uint8_t byte;                           /* Octet à transposer          */

    tmp = *value;

    do
    {
        byte = (tmp & 0x7f);
        tmp >>= 7;

        if (tmp != 0)
            byte |= 0x80;

        result = extend_packed_buffer(pbuf, &byte, sizeof(uint8_t), false);

    }
    while (result && tmp != 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur à consigner.                                  *
*                pbuf  = tampon de données à constituer. [OUT]                *
*                                                                             *
*  Description : Encode un nombre signé encodé au format LEB128.              *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_leb128(const leb128_t *value, packed_buffer_t *pbuf)
{

    bool result;                            /* Bilan à retourner           */
    uleb128_t tmp;                          /* Valeur modifiable           */
    bool more;                              /* Poursuite des traitements   */
    bool negative;                          /* Nature de la valeur         */
    uint8_t byte;                           /* Octet à transposer          */

    tmp = *value;

    more = true;
    negative = (*value < 0);

    while (more)
    {
        byte = (tmp & 0x7f);
        tmp >>= 7;

        /**
         * Propagation forcée du bit de signe pour les implémentations de
         * décalage basées sur une opération logique et non arithmétique.
         */

        if (negative)
            tmp |= (~0llu << (LEB128_BITS_COUNT - 7));

        /**
         * Le bit de signe n'est pas le bit de poids fort ici :
         * On travaille sur 7 bits, donc le masque est 0x40 !
         */

        if ((tmp == 0 && (byte & 0x40) == 0x00) || (tmp == -1 && (byte & 0x40) == 0x40))
            more = false;

        else
            byte |= 0x80;

        result = extend_packed_buffer(pbuf, &byte, sizeof(uint8_t), false);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur à constituer. [OUT]                           *
*                pbuf  = tampon de données à consulter.                       *
*                                                                             *
*  Description : Décode un nombre non signé encodé au format LEB128.          *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_uleb128(uleb128_t *value, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    unsigned int shift;                     /* Décalage à appliquer        */
    uint8_t byte;                           /* Octet à transposer          */

    result = true;

    *value = 0;

    shift = 0;

    while (true)
    {
        /* Encodage sur trop d'octets ? */
        if (shift > (7 * sizeof(uleb128_t)))
        {
            result = false;
            break;
        }

        result = extract_packed_buffer(pbuf, &byte, sizeof(uint8_t), false);
        if (!result) break;

        *value |= ((byte & 0x7f) << shift);

        if ((byte & 0x80) == 0x00)
            break;

        shift += 7;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value = valeur à constituer. [OUT]                           *
*                pbuf  = tampon de données à consulter.                       *
*                                                                             *
*  Description : Décode un nombre signé encodé au format LEB128.              *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_leb128(leb128_t *value, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    unsigned int shift;                     /* Décalage à appliquer        */
    uint8_t byte;                           /* Octet à transposer          */

    result = true;

    *value = 0;

    shift = 0;

    do
    {
        /* Encodage sur trop d'octets ? */
        if (shift > (7 * sizeof(leb128_t)))
        {
            result = false;
            break;
        }

        result = extract_packed_buffer(pbuf, &byte, sizeof(uint8_t), false);
        if (!result) break;

        *value |= ((byte & 0x7f) << shift);

        shift += 7;

    }
    while ((byte & 0x80) == 0x80);

    /**
     * Le bit de signe n'est pas le bit de poids fort ici :
     * On travaille sur 7 bits, donc le masque est 0x40 !
     */

    if (shift < LEB128_BITS_COUNT && (byte & 0x40) == 0x40)
        *value |= (~0llu << shift);

    return result;

}
