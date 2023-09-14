
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manual.h - définitions de macros pour la lecture manuelle de lexèmes
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _TOOLS_D2C_MANUAL_H
#define _TOOLS_D2C_MANUAL_H


#define read_block(tmp)                                                     \
    ({                                                                      \
        unsigned int __depth;                                               \
        bool __is_string;                                                   \
        char *__iter;                                                       \
                                                                            \
        __depth = 1;                                                        \
        __is_string = false;                                                \
                                                                            \
        for (__iter = temp; __depth > 0; __iter += (__depth > 0 ? 1 : 0))   \
        {                                                                   \
            *__iter = input();                                              \
                                                                            \
            switch (*__iter)                                                \
            {                                                               \
                case '"':                                                   \
                    __is_string = !__is_string;                             \
                    break;                                                  \
                                                                            \
                case '{':                                                   \
                    if (!__is_string) __depth++;                            \
                    break;                                                  \
                                                                            \
                case '}':                                                   \
                    if (!__is_string)                                       \
                    {                                                       \
                        __depth--;                                          \
                        if (__depth == 0) unput('}');                       \
                    }                                                       \
                    break;                                                  \
                                                                            \
            }                                                               \
                                                                            \
        }                                                                   \
                                                                            \
        *__iter = '\0';                                                     \
                                                                            \
    })


#endif  /* _TOOLS_D2C_MANUAL_H */
