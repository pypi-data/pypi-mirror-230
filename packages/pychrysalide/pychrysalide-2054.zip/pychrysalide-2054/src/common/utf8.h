
/* Chrysalide - Outil d'analyse de fichiers binaires
 * utf8.h - prototypes pour un support minimaliste mais adapté de l'encodage UTF-8
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


#ifndef _COMMON_UTF8_H
#define _COMMON_UTF8_H


#include <stdint.h>
#include <sys/types.h>



/* Représentation d'un caractère */
typedef uint32_t unichar_t;


/**
 * Erreurs qu'il est possible de rencontrer.
 */

#define UTF8_ERROR_MALFORMED ((unichar_t)-1)
#define UTF8_ERROR_TOO_LONG  ((unichar_t)-2)
#define UTF8_ERROR_TRUNCATED ((unichar_t)-3)
#define UTF8_ERROR_MISSING   ((unichar_t)-4)
#define UTF8_ERROR_WASTING   ((unichar_t)-5)

#define IS_UTF8_ERROR(v) (v & (1u << 31))


/* Procède à la lecture d'un caractère dans une chaîne en UTF-8. */
unichar_t decode_utf8_char(const unsigned char *, size_t, size_t *);

/* Procède à la lecture d'un caractère d'une chaîne en MUTF-8. */
unichar_t decode_mutf8_char(const unsigned char *, size_t, size_t *);



#endif  /* _COMMON_UTF8_H */
