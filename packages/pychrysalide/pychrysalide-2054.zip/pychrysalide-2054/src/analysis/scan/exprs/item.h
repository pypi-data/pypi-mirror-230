
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - prototypes pour la récupération d'un élément à partir d'une série
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


#ifndef _ANALYSIS_SCAN_EXPRS_ITEM_H
#define _ANALYSIS_SCAN_EXPRS_ITEM_H


#include "../expr.h"



#define G_TYPE_SCAN_SET_ITEM            g_scan_set_item_get_type()
#define G_SCAN_SET_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_SET_ITEM, GScanSetItem))
#define G_IS_SCAN_SET_ITEM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_SET_ITEM))
#define G_SCAN_SET_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_SET_ITEM, GScanSetItemClass))
#define G_IS_SCAN_SET_ITEM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_SET_ITEM))
#define G_SCAN_SET_ITEM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_SET_ITEM, GScanSetItemClass))


/* Accès à un élément donné d'une série établie (instance) */
typedef struct _GScanSetItem GScanSetItem;

/* Accès à un élément donné d'une série établie (classe) */
typedef struct _GScanSetItemClass GScanSetItemClass;


/* Indique le type défini pour la récupération d'un élément à partir d'une série. */
GType g_scan_set_item_get_type(void);

/* Met en place un accès à un élément donné d'une série. */
GScanExpression *g_scan_set_item_new(GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_ITEM_H */
