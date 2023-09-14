
/* Chrysalide - Outil d'analyse de fichiers binaires
 * relational.h - prototypes pour la gestion des opérations relationnelles
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


#ifndef _ANALYSIS_SCAN_EXPRS_RELATIONAL_H
#define _ANALYSIS_SCAN_EXPRS_RELATIONAL_H


#include "../expr.h"
#include "../../../glibext/comparison.h"



#define G_TYPE_SCAN_RELATIONAL_OPERATION            g_scan_relational_operation_get_type()
#define G_SCAN_RELATIONAL_OPERATION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_RELATIONAL_OPERATION, GScanRelationalOperation))
#define G_IS_SCAN_RELATIONAL_OPERATION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_RELATIONAL_OPERATION))
#define G_SCAN_RELATIONAL_OPERATION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_RELATIONAL_OPERATION, GScanRelationalOperationClass))
#define G_IS_SCAN_RELATIONAL_OPERATION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_RELATIONAL_OPERATION))
#define G_SCAN_RELATIONAL_OPERATION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_RELATIONAL_OPERATION, GScanRelationalOperationClass))


/* Opération relationnelle impliquant deux opérandes (instance) */
typedef struct _GScanRelationalOperation GScanRelationalOperation;

/* Opération relationnelle impliquant deux opérandes (classe) */
typedef struct _GScanRelationalOperationClass GScanRelationalOperationClass;


/* Indique le type défini pour une opération de relation entre expressions. */
GType g_scan_relational_operation_get_type(void);

/* Organise une opération relationnelle entre expressions. */
GScanExpression *g_scan_relational_operation_new(RichCmpOperation, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_RELATIONAL_H */
