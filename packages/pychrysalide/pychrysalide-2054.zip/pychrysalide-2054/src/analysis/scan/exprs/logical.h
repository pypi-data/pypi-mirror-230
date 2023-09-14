
/* Chrysalide - Outil d'analyse de fichiers binaires
 * logical.h - prototypes pour la gestion des opérations booléennes
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


#ifndef _ANALYSIS_SCAN_EXPRS_LOGICAL_H
#define _ANALYSIS_SCAN_EXPRS_LOGICAL_H


#include "../expr.h"



#define G_TYPE_BOOLEAN_OPERATION            g_scan_logical_operation_get_type()
#define G_SCAN_LOGICAL_OPERATION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BOOLEAN_OPERATION, GScanLogicalOperation))
#define G_IS_BOOLEAN_OPERATION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BOOLEAN_OPERATION))
#define G_SCAN_LOGICAL_OPERATION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BOOLEAN_OPERATION, GScanLogicalOperationClass))
#define G_IS_BOOLEAN_OPERATION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BOOLEAN_OPERATION))
#define G_SCAN_LOGICAL_OPERATION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BOOLEAN_OPERATION, GScanLogicalOperationClass))


/* Opération booléenne avec un ou deux opérandes (instance) */
typedef struct _GScanLogicalOperation GScanLogicalOperation;

/* Opération booléenne avec un ou deux opérandes (classe) */
typedef struct _GScanLogicalOperationClass GScanLogicalOperationClass;


/* Types d'opérations booléennes supportées */
typedef enum _BooleanOperationType
{
    BOT_AND,                                /* Opérateur binaire "and"     */
    BOT_OR,                                 /* Opérateur binaire "or"      */
    BOT_NOT,                                /* Opérateur unaire "not"      */

} BooleanOperationType;


/* Indique le type défini pour une opération booléenne sur expression(s). */
GType g_scan_logical_operation_get_type(void);

/* Organise un appel de fonction avec ses arguments. */
GScanExpression *g_scan_logical_operation_new(BooleanOperationType, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_LOGICAL_H */
