
/* Chrysalide - Outil d'analyse de fichiers binaires
 * arithmetic.h - prototypes pour la gestion des opérations arithmétiques
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


#ifndef _ANALYSIS_SCAN_EXPRS_ARITHMETIC_H
#define _ANALYSIS_SCAN_EXPRS_ARITHMETIC_H


#include "../expr.h"



#define G_TYPE_SCAN_ARITHMETIC_OPERATION            g_scan_arithmetic_operation_get_type()
#define G_SCAN_ARITHMETIC_OPERATION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_ARITHMETIC_OPERATION, GScanArithmeticOperation))
#define G_IS_SCAN_ARITHMETIC_OPERATION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_ARITHMETIC_OPERATION))
#define G_SCAN_ARITHMETIC_OPERATION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_ARITHMETIC_OPERATION, GScanArithmeticOperationClass))
#define G_IS_SCAN_ARITHMETIC_OPERATION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_ARITHMETIC_OPERATION))
#define G_SCAN_ARITHMETIC_OPERATION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_ARITHMETIC_OPERATION, GScanArithmeticOperationClass))


/* Opération arithmétique impliquant deux opérandes (instance) */
typedef struct _GScanArithmeticOperation GScanArithmeticOperation;

/* Opération arithmétique impliquant deux opérandes (classe) */
typedef struct _GScanArithmeticOperationClass GScanArithmeticOperationClass;


/* Type d'opération arithmétique */
typedef enum _ArithmeticExpressionOperator
{
    AEO_PLUS,                               /* Opération binaire "+"       */
    AEO_MINUS,                              /* Opération binaire "-"       */
    AEO_MUL,                                /* Opération binaire "*"       */
    AEO_DIV,                                /* Opération binaire "\"       */
    AEO_MOD,                                /* Opération binaire "%"       */

} ArithmeticExpressionOperator;


/* Indique le type défini pour une opération arithmétique entre expressions. */
GType g_scan_arithmetic_operation_get_type(void);

/* Organise une opération arithmétique entre expressions. */
GScanExpression *g_scan_arithmetic_operation_new(ArithmeticExpressionOperator, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_ARITHMETIC_H */
