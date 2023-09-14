
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strop-int.h - prototypes internes pour la gestion des opérations booléennes
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


#ifndef _ANALYSIS_SCAN_EXPRS_STROP_INT_H
#define _ANALYSIS_SCAN_EXPRS_STROP_INT_H


#include "strop.h"


#include "../expr-int.h"
#include "../../../common/extstr.h"



/* Opération booléenne avec un ou deux opérandes (instance) */
struct _GScanStringOperation
{
    GScanExpression parent;                 /* A laisser en premier        */

    StringOperationType type;               /* Type d'opération menée      */
    bool case_sensitive;                    /* Respect de la casse ?       */

    GScanExpression *left;                  /* Expression impactée #1      */
    GScanExpression *right;                 /* Expression impactée #2      */

};

/* Opération booléenne avec un ou deux opérandes (classe) */
struct _GScanStringOperationClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place une expression d'opération traite une chaîne. */
bool g_scan_string_operation_create(GScanStringOperation *, StringOperationType, GScanExpression *, GScanExpression *, bool);



#endif  /* _ANALYSIS_SCAN_EXPRS_STROP_INT_H */
