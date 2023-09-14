
/* Chrysalide - Outil d'analyse de fichiers binaires
 * literal.h - prototypes pour la représentation d'une valeur concrète
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


#ifndef _ANALYSIS_SCAN_EXPRS_LITERAL_H
#define _ANALYSIS_SCAN_EXPRS_LITERAL_H


#include <regex.h>
#include <stdbool.h>


#include "../expr.h"
#include "../../../common/szstr.h"



#define G_TYPE_SCAN_LITERAL_EXPRESSION            g_scan_literal_expression_get_type()
#define G_SCAN_LITERAL_EXPRESSION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_LITERAL_EXPRESSION, GScanLiteralExpression))
#define G_IS_SCAN_LITERAL_EXPRESSION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_LITERAL_EXPRESSION))
#define G_SCAN_LITERAL_EXPRESSION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_LITERAL_EXPRESSION, GScanLiteralExpressionClass))
#define G_IS_SCAN_LITERAL_EXPRESSION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_LITERAL_EXPRESSION))
#define G_SCAN_LITERAL_EXPRESSION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_LITERAL_EXPRESSION, GScanLiteralExpressionClass))


/* Expression portant une valeur concrète (instance) */
typedef struct _GScanLiteralExpression GScanLiteralExpression;

/* Expression portant une valeur concrète (classe) */
typedef struct _GScanLiteralExpressionClass GScanLiteralExpressionClass;


/* Types naturel équivalant à l'expression */
typedef enum _LiteralValueType
{
    LVT_BOOLEAN,                            /* Valeur booléenne            */
    LVT_SIGNED_INTEGER,                     /* Nombre entier 64 bits #1    */
    LVT_UNSIGNED_INTEGER,                   /* Nombre entier 64 bits #2    */
    LVT_STRING,                             /* Chaîne de caractères        */
    LVT_REG_EXPR,                           /* Expression rationnelle      */

} LiteralValueType;


/* Indique le type défini pour un appel de fonction enregistrée. */
GType g_scan_literal_expression_get_type(void);

/* Organise un appel de fonction avec ses arguments. */
GScanExpression *g_scan_literal_expression_new(LiteralValueType, ...);

/* Indique le type de valeur portée par une expression. */
LiteralValueType g_scan_literal_expression_get_value_type(const GScanLiteralExpression *);

/* Indique la valeur portée par une expression booléenne. */
bool g_scan_literal_expression_get_boolean_value(const GScanLiteralExpression *, bool *);

/* Indique la valeur portée par une expression d'entier. */
bool g_scan_literal_expression_get_signed_integer_value(const GScanLiteralExpression *, long long *);

/* Indique la valeur portée par une expression d'entier. */
bool g_scan_literal_expression_get_unsigned_integer_value(const GScanLiteralExpression *, unsigned long long *);

/* Indique la valeur portée par une expression de chaîne. */
bool g_scan_literal_expression_get_string_value(const GScanLiteralExpression *, const sized_string_t **);

/* Indique la valeur portée par une expression rationnelle. */
bool g_scan_literal_expression_get_regex_value(const GScanLiteralExpression *, const regex_t **);



#endif  /* _ANALYSIS_SCAN_EXPRS_LITERAL_H */
