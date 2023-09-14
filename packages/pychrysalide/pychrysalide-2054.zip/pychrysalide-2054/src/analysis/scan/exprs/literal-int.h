
/* Chrysalide - Outil d'analyse de fichiers binaires
 * literal-int.h - prototypes internes pour la représentation d'une valeur concrète
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_EXPRS_LITERAL_INT_H
#define _ANALYSIS_SCAN_EXPRS_LITERAL_INT_H


#include "literal.h"


#include "../expr-int.h"



/* Expression portant une valeur concrète (instance) */
struct _GScanLiteralExpression
{
    GScanExpression parent;                 /* A laisser en premier        */

    LiteralValueType value_type;            /* Type de valeur portée       */

    union
    {
        bool boolean;                       /* Valeur booléenne            */
        long long s_integer;                /* Valeur entière 64 bits      */
        unsigned long long u_integer;       /* Valeur entière 64 bits      */
        sized_string_t string;              /* Chaîne de caractères        */
        struct
        {
            char *regex;                    /* Formulation d'origine       */
            regex_t preg;                   /* Expression rationnelle      */
        };

    } value;

};

/* Expression portant une valeur concrète (classe) */
struct _GScanLiteralExpressionClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place une expression de valeur concrête. */
bool g_scan_literal_expression_create(GScanLiteralExpression *, LiteralValueType, ...);



#endif  /* _ANALYSIS_SCAN_EXPRS_LITERAL_INT_H */
