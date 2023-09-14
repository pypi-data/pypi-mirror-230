
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strop.h - prototypes pour la gestion des opérations booléennes
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


#ifndef _ANALYSIS_SCAN_EXPRS_STROP_H
#define _ANALYSIS_SCAN_EXPRS_STROP_H


#include "../expr.h"



#define G_TYPE_SCAN_STRING_OPERATION            g_scan_string_operation_get_type()
#define G_SCAN_STRING_OPERATION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_STRING_OPERATION, GScanStringOperation))
#define G_IS_SCAN_STRING_OPERATION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_STRING_OPERATION))
#define G_SCAN_STRING_OPERATION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_STRING_OPERATION, GScanStringOperationClass))
#define G_IS_SCAN_STRING_OPERATION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_STRING_OPERATION))
#define G_SCAN_STRING_OPERATION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_STRING_OPERATION, GScanStringOperationClass))


/* Opération booléenne avec un ou deux opérandes (instance) */
typedef struct _GScanStringOperation GScanStringOperation;

/* Opération booléenne avec un ou deux opérandes (classe) */
typedef struct _GScanStringOperationClass GScanStringOperationClass;


/* Types d'opérations booléennes supportées */
typedef enum _StringOperationType
{
    SOT_CONTAINS,                           /* Opérateurs "[i]contains"    */
    SOT_STARTSWITH,                         /* Opérateurs "[i]startswith"  */
    SOT_ENDSWITH,                           /* Opérateurs "[i]endswith"    */
    SOT_MATCHES,                            /* Opérateur "matches"         */
    SOT_IEQUALS,                            /* Opérateur "iequals"         */

} StringOperationType;


/* Indique le type défini pour une opération traitant une chaîne de caractères. */
GType g_scan_string_operation_get_type(void);

/* Organise un appel de fonction avec ses arguments. */
GScanExpression *g_scan_string_operation_new(StringOperationType, GScanExpression *, GScanExpression *, bool);



#endif  /* _ANALYSIS_SCAN_EXPRS_STROP_H */
