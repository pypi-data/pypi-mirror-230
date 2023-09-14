
/* Chrysalide - Outil d'analyse de fichiers binaires
 * relational-int.h - prototypes internes pour la gestion des opérations relationnelles
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


#ifndef _ANALYSIS_SCAN_EXPRS_RELATIONAL_INT_H
#define _ANALYSIS_SCAN_EXPRS_RELATIONAL_INT_H


#include "relational.h"


#include "../expr-int.h"



/* Opération relationnelle impliquant deux opérandes (instance) */
struct _GScanRelationalOperation
{
    GScanExpression parent;                 /* A laisser en premier        */

    RichCmpOperation rel_type;              /* Type de relation étudiée    */

    GScanExpression *left;                  /* Expression impactée #1      */
    GScanExpression *right;                 /* Expression impactée #2      */

};

/* Opération relationnelle impliquant deux opérandes (classe) */
struct _GScanRelationalOperationClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place une opération relationnelle entre expressions. */
bool g_scan_relational_operation_create(GScanRelationalOperation *, RichCmpOperation, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_RELATIONAL_INT_H */
