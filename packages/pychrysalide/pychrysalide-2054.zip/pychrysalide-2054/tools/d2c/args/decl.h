
/* Chrysalide - Outil d'analyse de fichiers binaires
 * decl.h - déclarations de prototypes utiles
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _TOOLS_D2C_ARGS_DECL_H
#define _TOOLS_D2C_ARGS_DECL_H


#include "manager.h"



/* Encapsulation de réponses multiples */
typedef struct _right_op_t
{
    char *func;                             /* Eventuelle fonction d'appel */

    union
    {
        arg_list_t *args;                   /* Liste d'arguments           */
        arg_expr_t *expr;                   /* Argument multi-usages       */
    };

} right_op_t;


/* Interprête des données relatives un opérande de droite. */
bool load_args_from_raw_line(right_op_t *, const char *);

/* Interprête des données relatives à un appel avec arguments. */
bool load_call_from_raw_line(right_op_t *, const char *);



#endif  /* _TOOLS_D2C_ARGS_DECL_H */
