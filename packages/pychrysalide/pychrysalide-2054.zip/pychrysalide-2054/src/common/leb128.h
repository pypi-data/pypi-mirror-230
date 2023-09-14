
/* Chrysalide - Outil d'analyse de fichiers binaires
 * leb128.h - prototypes pour le support des valeurs encodées au format LEB128.
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


#ifndef _COMMON_LEB128_H
#define _COMMON_LEB128_H


#include <stdbool.h>
#include <stdlib.h>


#include "packed.h"
#include "../arch/archbase.h"
#include "../arch/vmpa.h"



/* Nouveaux types */
typedef uint64_t uleb128_t;
typedef int64_t leb128_t;


/* Quantité de bits utilisés */
#define LEB128_BITS_COUNT (sizeof(leb128_t) * 8)

/* Récupération de la valeur absolue */
#define leb128_abs(v) llabs(v)

/* Valeurs minimales et maximales */
#define ULEB128_MIN UINT64_MIN
#define ULEB128_MAX UINT64_MAX
#define LEB128_MIN INT64_MIN
#define LEB128_MAX INT64_MAX


/* Lit un nombre non signé encodé au format LEB128. */
bool read_uleb128(uleb128_t *, const bin_t *, phys_t *, phys_t);

/* Lit un nombre signé encodé au format LEB128. */
bool read_leb128(leb128_t *, const bin_t *, phys_t *, phys_t);

/* Encode un nombre non signé encodé au format LEB128. */
bool pack_uleb128(const uleb128_t *, packed_buffer_t *);

/* Encode un nombre signé encodé au format LEB128. */
bool pack_leb128(const leb128_t *, packed_buffer_t *);

/* Décode un nombre non signé encodé au format LEB128. */
bool unpack_uleb128(uleb128_t *, packed_buffer_t *);

/* Décode un nombre signé encodé au format LEB128. */
bool unpack_leb128(leb128_t *, packed_buffer_t *);


#endif  /* _COMMON_LEB128_H */
