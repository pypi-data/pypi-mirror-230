
/* Chrysalide - Outil d'analyse de fichiers binaires
 * logical-int.h - prototypes internes pour la gestion des opérations booléennes
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


#ifndef _ANALYSIS_SCAN_EXPRS_LOGICAL_INT_H
#define _ANALYSIS_SCAN_EXPRS_LOGICAL_INT_H


#include "logical.h"


#include "../expr-int.h"



/* Opération booléenne avec un ou deux opérandes (instance) */
struct _GScanLogicalOperation
{
    GScanExpression parent;                 /* A laisser en premier        */

    BooleanOperationType type;              /* Type d'opération menée      */

    GScanExpression *first;                 /* Expression impactée #1      */
    GScanExpression *second;                /* Expression impactée #2      */

};

/* Opération booléenne avec un ou deux opérandes (classe) */
struct _GScanLogicalOperationClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place une expression d'opération booléenne. */
bool g_scan_logical_operation_create(GScanLogicalOperation *, BooleanOperationType, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_LOGICAL_INT_H */
