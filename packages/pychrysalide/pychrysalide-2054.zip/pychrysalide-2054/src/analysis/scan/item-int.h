
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item-int.h - prototypes internes pour la définition d'un élément appelable lors de l'exécution d'une règle
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


#ifndef _ANALYSIS_SCAN_ITEM_INT_H
#define _ANALYSIS_SCAN_ITEM_INT_H


#include "item.h"


#include <stdbool.h>



/* Indique le nom associé à une expression d'évaluation. */
typedef char * (* get_registered_item_name_fc) (const GRegisteredItem *);

/* Lance une résolution d'élément à solliciter. */
typedef bool (* resolve_registered_item_fc) (GRegisteredItem *, const char *, GScanContext *, GScanScope *, GRegisteredItem **);

/* Réduit une expression à une forme plus simple. */
typedef bool (* reduce_registered_item_fc) (GRegisteredItem *, GScanContext *, GScanScope *, GScanExpression **);

/* Effectue un appel à une fonction enregistrée. */
typedef bool (* run_registered_item_call_fc) (GRegisteredItem *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);


/* Expression d'évaluation généraliste (instance) */
struct _GRegisteredItem
{
    GObject parent;                         /* A laisser en premier        */

};

/* Expression d'évaluation généraliste (classe) */
struct _GRegisteredItemClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_registered_item_name_fc get_name;   /* Obtention du nom associé    */
    resolve_registered_item_fc resolve;     /* Opération de résolution     */
    reduce_registered_item_fc reduce;       /* Opération de réduction      */
    run_registered_item_call_fc run_call;   /* Appel à une fonction connue */

};



#endif  /* _ANALYSIS_SCAN_ITEM_INT_H */
