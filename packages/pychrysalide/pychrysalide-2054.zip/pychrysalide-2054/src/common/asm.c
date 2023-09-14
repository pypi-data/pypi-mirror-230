
/* Chrysalide - Outil d'analyse de fichiers binaires
 * asm.c - implémentations génériques de fonctionnalités spécifiques
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#include "asm.h"



/**
 * Indice du bit de poids fort dans un quartet.
 */

static const unsigned int _bval[16] = {

    0, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4

};


/**
 * Nombre de bits à 1 dans un octet.
 *
 * python3 -c "print(', '.join([ str(bin(n).count('1')) for n in range(256) ]))" | sed -re 's/(.{48})/\1\n/g' | sed 's/ $//'
 */

static const unsigned int _bcount[256] = {

    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8

};



/******************************************************************************
*                                                                             *
*  Paramètres  : v = valeur quelconque sur 32 bits.                           *
*                p = position du premier bit à 1 (poids fort). [OUT]          *
*                                                                             *
*  Description : Détermine l'indice du premier bit à 1, côté gauche.          *
*                                                                             *
*  Retour      : true si le nombre est différent de zéro, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool msb_32(uint32_t v, unsigned int *p)
{
    /* S'il n'y a aucun bit à 1... */
    if (v == 0) return false;

    /**
     * Il existe de nombreuses méthodes pour obtenir le résultat attendu
     * sans recourir à des extensions GCC ou à des instructions d'assembleur :
     *
     *  - http://stackoverflow.com/questions/2589096/find-most-significant-bit-left-most-that-is-set-in-a-bit-array
     *  - http://graphics.stanford.edu/~seander/bithacks.html#IntegerLogObvious
     *
     */

    *p = 0;

    if (v & 0xffff0000) { *p += 16 / 1; v >>= 16 / 1; }
    if (v & 0x0000ff00) { *p += 16 / 2; v >>= 16 / 2; }
    if (v & 0x000000f0) { *p += 16 / 4; v >>= 16 / 4; }

    *p += _bval[v];

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : v = valeur quelconque sur 64 bits.                           *
*                p = position du premier bit à 1 (poids fort). [OUT]          *
*                                                                             *
*  Description : Détermine l'indice du premier bit à 1, côté gauche.          *
*                                                                             *
*  Retour      : true si le nombre est différent de zéro, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool msb_64(uint64_t v, unsigned int *p)
{
    /* S'il n'y a aucun bit à 1... */
    if (v == 0) return false;

    /**
     * Cf. msb_32().
     */

    *p = 0;

    if (v & 0xffffffff00000000ull) { *p += 32 / 1; v >>= 32 / 1; }
    if (v & 0x00000000ffff0000ull) { *p += 32 / 2; v >>= 32 / 2; }
    if (v & 0x000000000000ff00ull) { *p += 32 / 4; v >>= 32 / 4; }
    if (v & 0x00000000000000f0ull) { *p += 32 / 8; v >>= 32 / 8; }

    *p += _bval[v];

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : v = valeur quelconque sur 32 bits.                           *
*                                                                             *
*  Description : Détermine le nombre de bits à 1 dans une valeur de 32 bits.  *
*                                                                             *
*  Retour      : Nombre de bits à 1.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int popcount_32(uint32_t v)
{
    unsigned int result;                    /* Valeur à retourner          */

    /**
     * Il existe de nombreuses méthodes pour obtenir le résultat attendu
     * sans recourir à des extensions GCC ou à des instructions d'assembleur :
     *
     *  - http://gurmeet.net/puzzles/fast-bit-counting-routines/
     *
     * On chosit un bon compromis entre efficacité et lecture.
     *
     */

    result = _bcount[v & 0xff]
           + _bcount[(v >>  8) & 0xff]
           + _bcount[(v >> 16) & 0xff]
           + _bcount[(v >> 24) & 0xff];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : v = valeur quelconque sur 64 bits.                           *
*                                                                             *
*  Description : Détermine le nombre de bits à 1 dans une valeur de 64 bits.  *
*                                                                             *
*  Retour      : Nombre de bits à 1.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int popcount_64(uint64_t v)
{
    unsigned int result;                    /* Valeur à retourner          */

    /**
     * Cf. popcount_32().
     */

    result = _bcount[v & 0xff]
           + _bcount[(v >>  8) & 0xff]
           + _bcount[(v >> 16) & 0xff]
           + _bcount[(v >> 24) & 0xff]
           + _bcount[(v >> 32) & 0xff]
           + _bcount[(v >> 40) & 0xff]
           + _bcount[(v >> 48) & 0xff]
           + _bcount[(v >> 56) & 0xff];

    return result;

}
