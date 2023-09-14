
/* Chrysalide - Outil d'analyse de fichiers binaires
 * endianness.h - prototypes pour la manipulation abstraite des nombres
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


#ifndef _COMMON_ENDIANNESS_H
#define _COMMON_ENDIANNESS_H


#include <stdbool.h>


#include "../arch/archbase.h"
#include "../arch/vmpa.h"



/* Type de boutismes existants */
typedef enum _SourceEndian
{
    SRE_LITTLE,                             /* Petits boutistes            */
    SRE_LITTLE_WORD,                        /* Moyens, façon Honeywell     */
    SRE_BIG_WORD,                           /* Moyens, façon PDP-11        */
    SRE_BIG                                 /* Gros boutistes              */

} SourceEndian;



/* --------------------------- CONVERSION ENTRE BOUTISMES --------------------------- */


/* Adapte un nombre sur 16 bits à un boutisme donné. */
uint16_t swap_u16(const uint16_t *, SourceEndian);

/* Adapte un nombre sur 16 bits à un boutisme donné. */
uint32_t swap_u32(const uint32_t *, SourceEndian);

/* Adapte un nombre sur 16 bits à un boutisme donné. */
uint64_t swap_u64(const uint64_t *, SourceEndian);


#define from_u16(v, e) swap_u16(v, e)
#define from_u32(v, e) swap_u32(v, e)
#define from_u64(v, e) swap_u64(v, e)


#define to_u16(v, e) swap_u16(v, e)
#define to_u32(v, e) swap_u32(v, e)
#define to_u64(v, e) swap_u64(v, e)



/* ------------------------- BOUTISME DES ENTREES / SORTIES ------------------------- */


/* Lit un nombre non signé sur 4 bits. */
bool read_u4(uint8_t *, const bin_t *, phys_t *, phys_t, bool *);

/* Lit un nombre non signé sur un octet. */
bool read_u8(uint8_t *, const bin_t *, phys_t *, phys_t);

/* Lit un nombre non signé sur deux octets. */
bool read_u16(uint16_t *, const bin_t *, phys_t *, phys_t, SourceEndian);

/* Lit un nombre non signé sur quatre octets. */
bool read_u32(uint32_t *, const bin_t *, phys_t *, phys_t, SourceEndian);

/* Lit un nombre non signé sur huit octets. */
bool read_u64(uint64_t *, const bin_t *, phys_t *, phys_t, SourceEndian);


#define read_s4(target, data, pos, len, low) read_u4((uint8_t *)target, data, pos, len, low)
#define read_s8(target, data, pos, len) read_u8((uint8_t *)target, data, pos, len)
#define read_s16(target, data, pos, len, endian) read_u16((uint16_t *)target, data, pos, len, endian)
#define read_s32(target, data, pos, len, endian) read_u32((uint32_t *)target, data, pos, len, endian)
#define read_s64(target, data, pos, len, endian) read_u64((uint64_t *)target, data, pos, len, endian)


/* Ecrit un nombre non signé sur n octets. */
bool _write_un(const bin_t *, size_t, bin_t *, off_t *, off_t, SourceEndian);


#define write_un(value, data, pos, len, endian, type)                       \
    ({                                                                      \
        type __tmp;                                                         \
        (void)(value == &__tmp);                                            \
        _write_un((bin_t *)value, sizeof(type), data, pos, len, endian);    \
    })


#define write_u8(value, data, pos, len, endian) write_un(value, data, pos, len, endian, uint8_t)
#define write_u16(value, data, pos, len, endian) write_un(value, data, pos, len, endian, uint16_t)
#define write_u32(value, data, pos, len, endian) write_un(value, data, pos, len, endian, uint32_t)
#define write_u64(value, data, pos, len, endian) write_un(value, data, pos, len, endian, uint64_t)

#define write_s8(value, data, pos, len, endian) write_un(value, data, pos, len, endian, sint8_t)
#define write_s16(value, data, pos, len, endian) write_un(value, data, pos, len, endian, sint16_t)
#define write_s32(value, data, pos, len, endian) write_un(value, data, pos, len, endian, sint32_t)
#define write_s64(value, data, pos, len, endian) write_un(value, data, pos, len, endian, sint64_t)


/* Lit un nombre hexadécimal non signé sur deux octets. */
bool strtou8(uint8_t *, const char *, size_t *, size_t, SourceEndian);

/* Lit un nombre hexadécimal non signé sur n octets. */
bool _strtoun(uint8_t, const char *, size_t *, size_t, SourceEndian, ...);


#define strtou32(target, data, pos, len, endian) _strtoun(4, data, pos, len, endian, target)



#endif  /* _COMMON_ENDIANNESS_H */
