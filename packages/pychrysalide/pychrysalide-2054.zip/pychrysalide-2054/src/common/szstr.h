
/* Chrysalide - Outil d'analyse de fichiers binaires
 * szstr.h - prototypes pour une manipulation de chaînes issues de Flex/Bison
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _COMMON_SZSTR_H
#define _COMMON_SZSTR_H


#include <string.h>
#include <sys/types.h>


#include "sort.h"
#include "../arch/archbase.h"



/* Structure associant une chaîne et sa taille */
typedef struct _sized_string_t
{
    union {
        const char *static_data;        /* Données non modifiées       */
        char *data;                     /* Chaîne de caractères        */
    };

    size_t len;                         /* Taille correspondante       */

} sized_string_t;


typedef sized_string_t sized_binary_t;


#define init_szstr(s)       \
    do                      \
    {                       \
        (s)->data = NULL;   \
        (s)->len = 0;       \
    }                       \
    while (0)

#define szstrdup(dst, src)                              \
    do                                                  \
    {                                                   \
        (dst)->data = malloc((src)->len);               \
        memcpy((dst)->data, (src)->data, (src)->len);   \
        (dst)->len = (src)->len;                        \
    }                                                   \
    while (0)

#define copy_szstr(d, s) (d) = (s);

#define exit_szstr(s)           \
    do                          \
    {                           \
        if ((s)->data != NULL)  \
        {                       \
            free((s)->data);    \
            init_szstr(s);      \
        }                       \
    }                           \
    while (0)

#define szstrcmp(s1, s2)                                            \
    ({                                                              \
        int __ret;                                                  \
        size_t __n;                                                 \
        __n = (s1)->len < (s2)->len ? (s1)->len : (s2)->len;        \
        __ret = strncmp((s1)->data, (s2)->data, __n);               \
        if (__ret == 0)                                             \
            __ret = sort_unsigned_long_long((s1)->len, (s2)->len);  \
        __ret;                                                      \
    })

#define szmemcmp(s1, s2)                                            \
    ({                                                              \
        int __ret;                                                  \
        size_t __n;                                                 \
        __n = (s1)->len < (s2)->len ? (s1)->len : (s2)->len;        \
        __ret = memcmp((s1)->data, (s2)->data, __n);                \
        if (__ret == 0)                                             \
            __ret = sort_unsigned_long_long((s1)->len, (s2)->len);  \
        __ret;                                                      \
    })



#endif  /* _COMMON_SZSTR_H */
