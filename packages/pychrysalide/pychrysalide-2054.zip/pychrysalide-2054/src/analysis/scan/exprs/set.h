
/* Chrysalide - Outil d'analyse de fichiers binaires
 * set.h - prototypes pour la base d'ensembles de valeurs diverses, de types hétérogènes ou homogènes
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


#ifndef _ANALYSIS_SCAN_EXPRS_SET_H
#define _ANALYSIS_SCAN_EXPRS_SET_H


#include "../expr.h"



#define G_TYPE_SCAN_GENERIC_SET            g_scan_generic_set_get_type()
#define G_SCAN_GENERIC_SET(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_GENERIC_SET, GScanGenericSet))
#define G_IS_SCAN_GENERIC_SET(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_GENERIC_SET))
#define G_SCAN_GENERIC_SET_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_GENERIC_SET, GScanGenericSetClass))
#define G_IS_SCAN_GENERIC_SET_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_GENERIC_SET))
#define G_SCAN_GENERIC_SET_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_GENERIC_SET, GScanGenericSetClass))


/* Base d'un ensemble d'éléments homogènes ou hétérogènes (instance) */
typedef struct _GScanGenericSet GScanGenericSet;

/* Base d'un ensemble d'éléments homogènes ou hétérogènes (classe) */
typedef struct _GScanGenericSetClass GScanGenericSetClass;


/* Indique le type défini pour une base d'ensembles d'éléments homogènes ou hétérogènes. */
GType g_scan_generic_set_get_type(void);

/* Constitue un ensemble d'éléments homogènes ou hétérogènes. */
GScanExpression *g_scan_generic_set_new(void);

/* Ajoute un nouvel élément à un ensemble. */
void g_scan_generic_set_add_item(GScanGenericSet *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_SET_H */
