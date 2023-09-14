
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expression.h - déclarations de prototypes utiles aux résolutions d'expressions
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _PLUGINS_KAITAI_EXPRESSION_H
#define _PLUGINS_KAITAI_EXPRESSION_H


#include <stdbool.h>
#include <sys/types.h>


#include <common/szstr.h>


#include "array.h"
#include "scope.h"
#include "stream.h"



/* Type de valeur résolue */
typedef enum _GrammarValueType
{
    GVT_ERROR,                              /* Erreur remontée             */
    GVT_UNSIGNED_INTEGER,                   /* Valeur entière #1           */
    GVT_SIGNED_INTEGER,                     /* Valeur entière #2           */
    GVT_FLOAT,                              /* Valeur fractionnée          */
    GVT_BOOLEAN,                            /* Valeur booléenne            */
    GVT_BYTES,                              /* Série d'octets dynamique    */
    GVT_ARRAY,                              /* Tableau d'éléments divers   */
    GVT_RECORD,                             /* Correspondance en place     */
    GVT_STREAM,                             /* Flux de données             */

} GrammarValueType;

/* Informations transportées par une expression */
typedef struct _resolved_value_t
{
    GrammarValueType type;                  /* Type de valeur portée       */

    union
    {
        unsigned long long unsigned_integer;/* Valeur entière #1           */
        signed long long signed_integer;    /* Valeur entière #2           */
        double floating_number;             /* Valeur à virgule flottante  */
        bool status;                        /* Valeur à deux états         */
        sized_string_t bytes;               /* Série d'octets              */

        GKaitaiArray *array;                /* Tableau d'éléments divers   */
        GMatchRecord *record;               /* Correspondance désignée     */
        GKaitaiStream *stream;              /* Flux de données pour Kaitai */

    };

} resolved_value_t;


#define COPY_RESOLVED_VALUE(dst, src)                   \
    do                                                  \
    {                                                   \
        (dst) = (src);                                  \
        switch ((dst).type)                             \
        {                                               \
            case GVT_ARRAY:                             \
                g_object_ref(G_OBJECT((dst).array));    \
                break;                                  \
            case GVT_RECORD:                            \
                g_object_ref(G_OBJECT((dst).record));   \
                break;                                  \
            case GVT_STREAM:                            \
                g_object_ref(G_OBJECT((dst).stream));   \
                break;                                  \
            default:                                    \
                break;                                  \
        }                                               \
    }                                                   \
    while (0)


#define EXIT_RESOLVED_VALUE(v)                          \
    switch ((v).type)                                   \
    {                                                   \
        case GVT_ARRAY:                                 \
            g_clear_object(&(v).array);                 \
            break;                                      \
        case GVT_RECORD:                                \
            g_clear_object(&(v).record);                \
            break;                                      \
        case GVT_STREAM:                                \
            g_clear_object(&(v).stream);                \
            break;                                      \
        default:                                        \
            break;                                      \
    }


/* Interprète une expression en une valeur quelconque. */
bool resolve_kaitai_expression_as_any(const kaitai_scope_t *, const char *, size_t, resolved_value_t *);

/* Interprète une expression en valeur ciblée entière. */
bool resolve_kaitai_expression_as_integer(const kaitai_scope_t *, const char *, size_t, resolved_value_t *);

/* Interprète une expression en valeur ciblée booléenne. */
bool resolve_kaitai_expression_as_boolean(const kaitai_scope_t *, const char *, size_t, resolved_value_t *);

/* Interprète une expression en série d'octets. */
bool resolve_kaitai_expression_as_bytes(const kaitai_scope_t *, const char *, size_t, resolved_value_t *);

/* Interprète une expression en flux de données pour Kaitai. */
bool resolve_kaitai_expression_as_stream(const kaitai_scope_t *, const char *, size_t, GKaitaiStream **);



#endif  /* _PLUGINS_KAITAI_EXPRESSION_H */
