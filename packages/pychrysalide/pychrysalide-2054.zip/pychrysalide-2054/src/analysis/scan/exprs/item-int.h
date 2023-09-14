
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item-int.h - prototypes internes pour la récupération d'un élément à partir d'une série
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


#ifndef _ANALYSIS_SCAN_EXPRS_ITEM_INT_H
#define _ANALYSIS_SCAN_EXPRS_ITEM_INT_H


#include "item.h"


#include "../expr-int.h"



/* Accès à un élément donné d'une série établie (instance) */
struct _GScanSetItem
{
    GScanExpression parent;                 /* A laisser en premier        */

    GScanExpression *set;                   /* Série d'éléments à consulter*/
    GScanExpression *index;                 /* Indice de l'élément visé    */

};

/* Accès à un élément donné d'une série établie (classe) */
struct _GScanSetItemClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place un accès à un élément donné d'une série. */
bool g_scan_set_item_create(GScanSetItem *, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_ITEM_INT_H */
