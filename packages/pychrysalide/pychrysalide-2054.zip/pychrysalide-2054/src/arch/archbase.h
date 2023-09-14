
/* Chrysalide - Outil d'analyse de fichiers binaires
 * archbase.h - prototypes des définitions de base pour les architectures
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


#ifndef _ARCH_ARCHBASE_H
#define _ARCH_ARCHBASE_H


#include <stdint.h>
#include <sys/types.h>



#define OFF_FMT     "%llu"
#define OFF_CAST(v) ((unsigned long long)v)


/* Octet de données binaires */
typedef uint8_t bin_t;

/* Adresse mémoire ou position physique */
typedef uint64_t vmpa_t;


#define VMPA_MAX        0xffffffffffffffffull
#define VMPA_INVALID    0xffffffffffffffffull

#define VMPA_FMT        "0x%llx"
#define VMPA_FMT_LONG   "0x%08llx"
#define VMPA_CAST(v)    ((unsigned long long)v)
#define VMPA_MAX_SIZE   19


/* Taille des données intégrées */
typedef enum _MemoryDataSize
{
    MDS_UNDEFINED,                          /* Taille non définie          */

    MDS_4_BITS_UNSIGNED     = 0x01,         /* Opérande sur 4 bits n.-s.   */
    MDS_8_BITS_UNSIGNED     = 0x02,         /* Opérande sur 8 bits n.-s.   */
    MDS_16_BITS_UNSIGNED    = 0x03,         /* Opérande sur 16 bits n.-s.  */
    MDS_32_BITS_UNSIGNED    = 0x04,         /* Opérande sur 32 bits n.-s.  */
    MDS_64_BITS_UNSIGNED    = 0x05,         /* Opérande sur 64 bits n.-s.  */

    MDS_4_BITS_SIGNED       = 0x81,         /* Opérande sur 4 bits  signés */
    MDS_8_BITS_SIGNED       = 0x82,         /* Opérande sur 8 bits  signés */
    MDS_16_BITS_SIGNED      = 0x83,         /* Opérande sur 16 bits signés */
    MDS_32_BITS_SIGNED      = 0x84,         /* Opérande sur 32 bits signés */
    MDS_64_BITS_SIGNED      = 0x85          /* Opérande sur 64 bits signés */

} MemoryDataSize;


#define MDS_RANGE(mds) ((mds & 0xf) - 1)
#define MDS_SIGN 0x80
#define MDS_IS_SIGNED(mds) (mds & MDS_SIGN)


#define MDS_FROM_BYTES(sz)                          \
    ({                                              \
        MemoryDataSize __result;                    \
        switch (sz)                                 \
        {                                           \
             case 1:                                \
                 __result = MDS_8_BITS_UNSIGNED;    \
                 break;                             \
             case 2:                                \
                 __result = MDS_16_BITS_UNSIGNED;   \
                 break;                             \
             case 3 ... 4:                          \
                 __result = MDS_32_BITS_UNSIGNED;   \
                 break;                             \
             case 5 ... 8:                          \
                 __result = MDS_64_BITS_UNSIGNED;   \
                 break;                             \
             default:                               \
                 __result = MDS_UNDEFINED;          \
                 break;                             \
        }                                           \
        __result;                                   \
    })


#define MDS_4_BITS  MDS_4_BITS_UNSIGNED
#define MDS_8_BITS  MDS_8_BITS_UNSIGNED
#define MDS_16_BITS MDS_16_BITS_UNSIGNED
#define MDS_32_BITS MDS_32_BITS_UNSIGNED
#define MDS_64_BITS MDS_64_BITS_UNSIGNED



/* Etablit la comparaison entre deux adresses. */
int compare_vmpa(const vmpa_t *, const vmpa_t *);

/* Transforme une adresse en chaîne de caractères. */
size_t vmpa_to_string(vmpa_t, MemoryDataSize, char [VMPA_MAX_SIZE]);

/* Transforme une chaîne de caractères en adresse. */
vmpa_t string_to_vmpa(const char *);



#endif  /* _ARCH_ARCHBASE_H */
