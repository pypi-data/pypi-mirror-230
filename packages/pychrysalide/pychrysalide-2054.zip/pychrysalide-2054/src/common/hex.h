
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.h - prototypes pour la construction et l'interprétation de chaînes hexadécimales
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


#ifndef _COMMON_HEX_H
#define _COMMON_HEX_H


#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>



/* Encode des données en chaîne hexadécimale. */
void encode_hex(const char *, size_t, bool, char *);

/* Décode un caractère hexadécimal. */
bool decode_hex_digit(const char *, uint8_t *);



#endif  /* _COMMON_HEX_H */
