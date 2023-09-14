
/* Chrysalide - Outil d'analyse de fichiers binaires
 * set-int.h - prototypes internes pour la base d'ensembles de valeurs diverses, de types hétérogènes ou homogènes
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


#ifndef _ANALYSIS_SCAN_EXPRS_SET_INT_H
#define _ANALYSIS_SCAN_EXPRS_SET_INT_H


#include "set.h"


#include "../expr-int.h"



/* Base d'un ensemble d'éléments homogènes ou hétérogènes (instance) */
struct _GScanGenericSet
{
    GScanExpression parent;                 /* A laisser en premier        */

    GScanExpression **items;                /* Liste d'éléments embarqués  */
    size_t count;                           /* Quantité de ces éléments    */

};

/* Base d'un ensemble d'éléments homogènes ou hétérogènes (classe) */
struct _GScanGenericSetClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place un ensemble d'éléments homogènes ou hétérogènes. */
bool g_scan_generic_set_create(GScanGenericSet *);



#endif  /* _ANALYSIS_SCAN_EXPRS_SET_INT_H */
