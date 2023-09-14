
/* Chrysalide - Outil d'analyse de fichiers binaires
 * utils.h - prototypes pour les fonctions qui simplifient la vie dans les interactions avec un serveur GDB
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


#ifndef _DEBUG_GDBRSP_UTILS_H
#define _DEBUG_GDBRSP_UTILS_H


#include <stdbool.h>
#include <stdint.h>
#include <sys/types.h>



/* Indique si les données correspondent à un code d'erreur. */
bool is_error_code(const char *, size_t);

/* Relit une valeur sur 8 bits et deux lettres. */
bool read_fixed_byte(const char *, size_t, uint8_t *);

/* Traduit en valeur sur XX bits une forme textuelle. */
bool hex_to_any_u(const char *, size_t, ...);

#define hex_to_u8(h, v)  hex_to_any_u(h, 1, v)
#define hex_to_u16(h, v) hex_to_any_u(h, 2, v)
#define hex_to_u32(h, v) hex_to_any_u(h, 4, v)
#define hex_to_u64(h, v) hex_to_any_u(h, 8, v)

/* Traduit une valeur sur XX bits en forme textuelle. */
bool any_u_to_hex(size_t, char [17], ...);

#define u8_to_hex(v, h)  any_u_to_hex(1, h, v)
#define u16_to_hex(v, h) any_u_to_hex(2, h, v)
#define u32_to_hex(v, h) any_u_to_hex(4, h, v)
#define u64_to_hex(v, h) any_u_to_hex(8, h, v)



#endif  /* _DEBUG_GDBRSP_UTILS_H */
