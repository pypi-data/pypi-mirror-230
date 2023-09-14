
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - prototypes pour la définition d'un élément appelable lors de l'exécution d'une règle
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_ITEM_H
#define _ANALYSIS_SCAN_ITEM_H


#include <glib-object.h>
#include <stdbool.h>


#include "context.h"
#include "expr.h"



#define G_TYPE_REGISTERED_ITEM            g_registered_item_get_type()
#define G_REGISTERED_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_REGISTERED_ITEM, GRegisteredItem))
#define G_IS_REGISTERED_ITEM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_REGISTERED_ITEM))
#define G_REGISTERED_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_REGISTERED_ITEM, GRegisteredItemClass))
#define G_IS_REGISTERED_ITEM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_REGISTERED_ITEM))
#define G_REGISTERED_ITEM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_REGISTERED_ITEM, GRegisteredItemClass))


/* Expression d'évaluation généraliste (instance) */
typedef struct _GRegisteredItem GRegisteredItem;

/* Expression d'évaluation généraliste (classe) */
typedef struct _GRegisteredItemClass GRegisteredItemClass;


/* Indique le type défini pour un élément appelable et enregistré. */
GType g_registered_item_get_type(void);

/* Indique le nom associé à une expression d'évaluation. */
char *g_registered_item_get_name(const GRegisteredItem *);

/* Lance une résolution d'élément à solliciter. */
bool g_registered_item_resolve(GRegisteredItem *, const char *, GScanContext *, GScanScope *, GRegisteredItem **);

/* Réduit une expression à une forme plus simple. */
bool g_registered_item_reduce(GRegisteredItem *, GScanContext *, GScanScope *, GScanExpression **);

/* Effectue un appel à une fonction enregistrée. */
bool g_registered_item_run_call(GRegisteredItem *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



#endif  /* _ANALYSIS_SCAN_ITEM_H */
