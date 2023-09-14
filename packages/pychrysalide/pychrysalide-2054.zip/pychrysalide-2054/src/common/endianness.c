
/* Chrysalide - Outil d'analyse de fichiers binaires
 * endianness.c - manipulation abstraite des nombres
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "endianness.h"


#include <assert.h>
#include <stdarg.h>
#include <string.h>



/**
 * Mutualisation des aiguillages...
 */

#if __BYTE_ORDER != __LITTLE_ENDIAN && __BYTE_ORDER != __BIG_ENDIAN

    /* __PDP_ENDIAN et Cie... */
#   error "Congratulations! Your byte order is not supported!"

#endif



/* ---------------------------------------------------------------------------------- */
/*                             CONVERSION ENTRE BOUTISMES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : value  = valeur d'origine à manipuler.                       *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Adapte un nombre sur 16 bits à un boutisme donné.            *
*                                                                             *
*  Retour      : Valeur transformée au besoin.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint16_t swap_u16(const uint16_t *value, SourceEndian endian)
{
    uint16_t result;                        /* Valeur à retourner          */

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            result = *value;

#elif __BYTE_ORDER == __BIG_ENDIAN

            result = ((*value >> 0) & 0xff) << 8 | ((*value >> 8) & 0xff) << 0;

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            result = ((*value >> 0) & 0xff) << 8 | ((*value >> 8) & 0xff) << 0;

#elif __BYTE_ORDER == __BIG_ENDIAN

            result = *value;

#endif

            break;

        default:
            assert(false);
            result = -1;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value  = valeur d'origine à manipuler.                       *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Adapte un nombre sur 16 bits à un boutisme donné.            *
*                                                                             *
*  Retour      : Valeur transformée au besoin.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t swap_u32(const uint32_t *value, SourceEndian endian)
{
    uint32_t result;                        /* Valeur à retourner          */

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            result = *value;

#elif __BYTE_ORDER == __BIG_ENDIAN

            result = ((*value >>  0) & 0xff) << 24 | ((*value >>  8) & 0xff) << 16
                   | ((*value >> 16) & 0xff) << 8  | ((*value >> 24) & 0xff) << 0;

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            result = ((*value >>  0) & 0xff) << 24 | ((*value >>  8) & 0xff) << 16
                   | ((*value >> 16) & 0xff) << 8  | ((*value >> 24) & 0xff) << 0;

#elif __BYTE_ORDER == __BIG_ENDIAN

            result = *value;

#endif

            break;

        default:
            assert(false);
            result = -1;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value  = valeur d'origine à manipuler.                       *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Adapte un nombre sur 16 bits à un boutisme donné.            *
*                                                                             *
*  Retour      : Valeur transformée au besoin.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint64_t swap_u64(const uint64_t *value, SourceEndian endian)
{
    uint64_t result;                        /* Valeur à retourner          */

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            result = *value;

#elif __BYTE_ORDER == __BIG_ENDIAN

            result = ((*value >>  0) & 0xff) << 56 | ((*value >>  8) & 0xff) << 48
                   | ((*value >> 16) & 0xff) << 40 | ((*value >> 24) & 0xff) << 32
                   | ((*value >> 32) & 0xff) << 24 | ((*value >> 40) & 0xff) << 16
                   | ((*value >> 48) & 0xff) << 8  | ((*value >> 56) & 0xff) << 0;

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            result = ((*value >>  0) & 0xff) << 56 | ((*value >>  8) & 0xff) << 48
                   | ((*value >> 16) & 0xff) << 40 | ((*value >> 24) & 0xff) << 32
                   | ((*value >> 32) & 0xff) << 24 | ((*value >> 40) & 0xff) << 16
                   | ((*value >> 48) & 0xff) << 8  | ((*value >> 56) & 0xff) << 0;

#elif __BYTE_ORDER == __BIG_ENDIAN

            result = *value;

#endif

            break;

        default:
            assert(false);
            result = -1;
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           BOUTISME DES ENTREES / SORTIES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                low    = position éventuelle des 4 bits visés. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur 4 bits.                          *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_u4(uint8_t *target, const bin_t *data, phys_t *pos, phys_t end, bool *low)
{
    if (end < 1) return false;
    if (*pos > (end - 1)) return false;

    if (*low)
    {
        *target = data[*pos] & 0x0f;
        *low = false;
    }
    else
    {
        *target = (data[*pos] & 0xf0) >> 4;
        *low = true;
        *pos += 1;
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                                                                             *
*  Description : Lit un nombre non signé sur un octet.                        *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_u8(uint8_t *target, const bin_t *data, phys_t *pos, phys_t end)
{
    if (end < 1) return false;
    if (*pos > (end - 1)) return false;

    *target = data[*pos];

    *pos += 1;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Lit un nombre non signé sur deux octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_u16(uint16_t *target, const bin_t *data, phys_t *pos, phys_t end, SourceEndian endian)
{
    if (end < 2) return false;
    if (*pos > (end - 2)) return false;

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos] | (uint16_t)data[*pos + 1] << 8;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos + 1] | (uint16_t)data[*pos] << 8;

#endif

            break;

        case SRE_LITTLE_WORD:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos] << 8 | (uint16_t)data[*pos + 1];

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos + 1] << 8 | (uint16_t)data[*pos];

#endif

            break;

        case SRE_BIG_WORD:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos + 1] << 8 | (uint16_t)data[*pos];

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos] << 8 | (uint16_t)data[*pos + 1];

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos + 1] | (uint16_t)data[*pos] << 8;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos] | (uint16_t)data[*pos + 1] << 8;

#endif

            break;

        default:
            return false;
            break;

    }

    *pos += 2;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Lit un nombre non signé sur quatre octets.                   *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_u32(uint32_t *target, const bin_t *data, phys_t *pos, phys_t end, SourceEndian endian)
{
    if (end < 4) return false;
    if (*pos > (end - 4)) return false;

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos] | (uint32_t)data[*pos + 1] << 8;
            *target |= data[*pos + 2] << 16 | (uint32_t)data[*pos + 3] << 24;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos + 3] | (uint32_t)data[*pos + 2] << 8;
            *target |= data[*pos + 1] << 16 | (uint32_t)data[*pos] << 24;

#endif

            break;

        case SRE_LITTLE_WORD:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos] << 8 | (uint32_t)data[*pos + 1];
            *target |= data[*pos + 2] << 24 | (uint32_t)data[*pos + 3] << 16;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos + 3] << 8 | (uint32_t)data[*pos + 2];
            *target |= data[*pos + 1] << 24 | (uint32_t)data[*pos] << 16;

#endif

            break;

        case SRE_BIG_WORD:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos + 3] << 8 | (uint32_t)data[*pos + 2];
            *target |= data[*pos + 1] << 24 | (uint32_t)data[*pos] << 16;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos] << 8 | (uint32_t)data[*pos + 1];
            *target |= data[*pos + 2] << 24 | (uint32_t)data[*pos + 3] << 16;

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = data[*pos + 3] | (uint32_t)data[*pos + 2] << 8;
            *target |= data[*pos + 1] << 16 | (uint32_t)data[*pos] << 24;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = data[*pos] | (uint32_t)data[*pos + 1] << 8;
            *target |= data[*pos + 2] << 16 | (uint32_t)data[*pos + 3] << 24;

#endif

            break;

    default:
        return false;
        break;

    }

    *pos += 4;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Lit un nombre non signé sur huit octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool read_u64(uint64_t *target, const bin_t *data, phys_t *pos, phys_t end, SourceEndian endian)
{
    if (end < 8) return false;
    if (*pos > (end - 8)) return false;

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = (uint64_t)data[*pos] | (uint64_t)data[*pos + 1] << 8;
            *target |= (uint64_t)data[*pos + 2] << 16 | (uint64_t)data[*pos + 3] << 24;
            *target |= (uint64_t)data[*pos + 4] << 32 | (uint64_t)data[*pos + 5] << 40;
            *target |= (uint64_t)data[*pos + 6] << 48 | (uint64_t)data[*pos + 7] << 56;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = (uint64_t)data[*pos + 7] | (uint64_t)data[*pos + 6] << 8;
            *target |= (uint64_t)data[*pos + 5] << 16 | (uint64_t)data[*pos + 4] << 24;
            *target |= (uint64_t)data[*pos + 3] << 32 | (uint64_t)data[*pos + 2] << 40;
            *target |= (uint64_t)data[*pos + 1] << 48 | (uint64_t)data[*pos] << 56;

#endif

            break;

        case SRE_LITTLE_WORD:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = (uint64_t)data[*pos] << 8 | (uint64_t)data[*pos + 1];
            *target |= (uint64_t)data[*pos + 2] << 24 | (uint64_t)data[*pos + 3] << 16;
            *target |= (uint64_t)data[*pos + 4] << 40 | (uint64_t)data[*pos + 5] << 32;
            *target |= (uint64_t)data[*pos + 6] << 56 | (uint64_t)data[*pos + 7] << 48;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = (uint64_t)data[*pos + 7] << 8 | (uint64_t)data[*pos + 6];
            *target |= (uint64_t)data[*pos + 5] << 24 | (uint64_t)data[*pos + 4] << 16;
            *target |= (uint64_t)data[*pos + 3] << 40 | (uint64_t)data[*pos + 2] << 32;
            *target |= (uint64_t)data[*pos + 1] << 56 | (uint64_t)data[*pos] << 48;

#endif

            break;

        case SRE_BIG_WORD:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = (uint64_t)data[*pos + 7] << 8 | (uint64_t)data[*pos + 6];
            *target |= (uint64_t)data[*pos + 5] << 24 | (uint64_t)data[*pos + 4] << 16;
            *target |= (uint64_t)data[*pos + 3] << 40 | (uint64_t)data[*pos + 2] << 32;
            *target |= (uint64_t)data[*pos + 1] << 56 | (uint64_t)data[*pos] << 48;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = (uint64_t)data[*pos] << 8| (uint64_t)data[*pos + 1];
            *target |= (uint64_t)data[*pos + 2] << 24 | (uint64_t)data[*pos + 3] << 16;
            *target |= (uint64_t)data[*pos + 4] << 40 | (uint64_t)data[*pos + 5] << 32;
            *target |= (uint64_t)data[*pos + 6] << 56 | (uint64_t)data[*pos + 7] << 48;

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            *target = (uint64_t)data[*pos + 7] | (uint64_t)data[*pos + 6] << 8;
            *target |= (uint64_t)data[*pos + 5] << 16 | (uint64_t)data[*pos + 4] << 24;
            *target |= (uint64_t)data[*pos + 3] << 32 | (uint64_t)data[*pos + 2] << 40;
            *target |= (uint64_t)data[*pos + 1] << 48 | (uint64_t)data[*pos] << 56;

#elif __BYTE_ORDER == __BIG_ENDIAN

            *target = (uint64_t)data[*pos] | (uint64_t)data[*pos + 1] << 8;
            *target |= (uint64_t)data[*pos + 2] << 16 | (uint64_t)data[*pos + 3] << 24;
            *target |= (uint64_t)data[*pos + 4] << 32 | (uint64_t)data[*pos + 5] << 40;
            *target |= (uint64_t)data[*pos + 6] << 48 | (uint64_t)data[*pos + 7] << 56;

#endif

            break;

        default:
            return false;
            break;

    }

    *pos += 8;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : value  = source de la valeur à transcrire.                   *
*                size   = taille de cette source de données.                  *
*                data   = flux de données à modifier. [OUT]                   *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Ecrit un nombre non signé sur n octets.                      *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _write_un(const bin_t *value, size_t size, bin_t *data, off_t *pos, off_t end, SourceEndian endian)
{
    size_t i;                               /* Boucle de parcours          */

    if (end < size) return false;
    if (*pos > (end - size)) return false;

    switch (endian)
    {
        case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            memcpy(&data[*pos], value, size);
            (*pos) += size;

#elif __BYTE_ORDER == __BIG_ENDIAN

            for (i = 0; i < size; i++, (*pos)++)
                *(data + *pos) = *(value + size - i - 1);

#endif

            break;

        case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

            for (i = 0; i < size; i++, (*pos)++)
                *(data + *pos) = *(value + size - i - 1);

#elif __BYTE_ORDER == __BIG_ENDIAN

            memcpy(&data[*pos], value, size);
            (*pos) += size;

#endif

            break;

        default:
            return false;
            break;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = lieu d'enregistrement de la lecture. [OUT]          *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                endian = ordre des bits dans la source.                      *
*                                                                             *
*  Description : Lit un nombre hexadécimal non signé sur deux octets.         *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool strtou8(uint8_t *target, const char *data, size_t *pos, size_t end, SourceEndian endian)
{
    size_t i;                               /* Boucle de parcours          */

    if (end < 2) return false;
    if (*pos > (end - 2)) return false;

    *target = 0;

    for (i = 0; i < 2; i++)
        switch (data[*pos + i])
        {
            case '0' ... '9':
                *target |= ((data[*pos + i] - '0') << (4 * (1 - i)));
                break;

            case 'A' ... 'F':
                *target |= ((data[*pos + i] + 10 - 'A') << (4 * (1 - i)));
                break;

            case 'a' ... 'f':
                *target |= ((data[*pos + i] + 10 - 'a') << (4 * (1 - i)));
                break;

        }

    *pos += 2;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : n      = nombre d'octets constituant le nombre à lire.       *
*                data   = flux de données à analyser.                         *
*                pos    = position courante dans ce flux. [OUT]               *
*                end    = limite des données à analyser.                      *
*                endian = ordre des bits dans la source.                      *
*                ...    = lieu d'enregistrement de la lecture. [OUT]          *
*                                                                             *
*  Description : Lit un nombre hexadécimal non signé sur n octets.            *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _strtoun(uint8_t n, const char *data, size_t *pos, size_t end, SourceEndian endian, ...)
{
    bool result;                            /* Bilan à renvoyer            */
    va_list ap;                             /* Arguments variables         */
    uint8_t *target8;                       /* Enregistrement sur 8 bits   */
    uint16_t *target16;                     /* Enregistrement sur 16 bits  */
    uint32_t *target32;                     /* Enregistrement sur 32 bits  */
    uint64_t *target64;                     /* Enregistrement sur 64 bits  */
    uint8_t i;                              /* Boucle de parcours #1       */
    size_t j;                               /* Boucle de parcours #2       */
    uint8_t tmp;                            /* Valeur temporaire de 8 bits */

    if (end < (n * 2)) return false;
    if (*pos > (end - (n * 2))) return false;

    /* Récupération de la destination */

    va_start(ap, endian);

    switch (n)
    {
        case 1:
            target8 = va_arg(ap, uint8_t *);
            *target8 = 0;
            target64 = (uint64_t *)target8;
            break;
        case 2:
            target16 = va_arg(ap, uint16_t *);
            *target16 = 0;
            target64 = (uint64_t *)target16;
            break;
        case 4:
            target32 = va_arg(ap, uint32_t *);
            *target32 = 0;
            target64 = (uint64_t *)target32;
            break;
        case 8:
            target64 = va_arg(ap, uint64_t *);
            *target64 = 0ull;
            break;
        default:
            va_end(ap);
            return false;
            break;
    }

    va_end(ap);

    /* Lecture des données */

    result = true;

    for (i = 0; i < n && result; i++)
    {
        tmp = 0;

        for (j = 0; j < 2 && result; j++)
            switch (data[*pos + j])
            {
                case '0' ... '9':
                    tmp |= ((data[*pos + j] - '0') << (4 * (1 - j)));
                    break;

                case 'A' ... 'F':
                    tmp |= ((data[*pos + j] + 10 - 'A') << (4 * (1 - j)));
                    break;

                case 'a' ... 'f':
                    tmp |= ((data[*pos + j] + 10 - 'a') << (4 * (1 - j)));
                    break;

                default:
                    result = false;
                    break;

            }

        *pos += 2;

        switch (endian)
        {
            case SRE_LITTLE:

#if __BYTE_ORDER == __LITTLE_ENDIAN

                *target64 |= ((uint64_t)tmp) << (8 * i);

#elif __BYTE_ORDER == __BIG_ENDIAN

                *target64 |= ((uint64_t)tmp) << (8 * (n - 1 - i));

#endif

                break;

            case SRE_BIG:

#if __BYTE_ORDER == __LITTLE_ENDIAN

                *target64 |= ((uint64_t)tmp) << (8 * (n - 1 - i));

#elif __BYTE_ORDER == __BIG_ENDIAN

                *target64 |= ((uint64_t)tmp) << (8 * i);

#endif

                break;

        default:
            return false;
            break;

        }

    }

    return result;

}
