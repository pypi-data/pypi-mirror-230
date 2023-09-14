
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comparison.h - prototypes pour les opérations de comparaison d'objets
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


#ifndef _GLIBEXT_COMPARISON_H
#define _GLIBEXT_COMPARISON_H


#include <glib-object.h>
#include <stdbool.h>



#define G_TYPE_COMPARABLE_ITEM             (g_comparable_item_get_type())
#define G_COMPARABLE_ITEM(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_COMPARABLE_ITEM, GComparableItem))
#define G_COMPARABLE_ITEM_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_COMPARABLE_ITEM, GComparableItemIface))
#define G_IS_COMPARABLE_ITEM(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_COMPARABLE_ITEM))
#define G_IS_COMPARABLE_ITEM_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_COMPARABLE_ITEM))
#define G_COMPARABLE_ITEM_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_COMPARABLE_ITEM, GComparableItemIface))


/* Instance d'élément comparable (coquille vide) */
typedef struct _GComparableItem GComparableItem;

/* Instance d'élément comparable (interface) */
typedef struct _GComparableItemIface GComparableItemIface;


/* Modes de comparaison */
typedef enum _RichCmpOperation
{
    RCO_LT,                                 /* Equivalent de '<'           */
    RCO_LE,                                 /* Equivalent de '<='          */
    RCO_EQ,                                 /* Equivalent de '=='          */
    RCO_NE,                                 /* Equivalent de '!='          */
    RCO_GT,                                 /* Equivalent de '>'           */
    RCO_GE,                                 /* Equivalent de '>°'          */

} RichCmpOperation;

/* Détermination d'un besoin de comparaison supplémentaire */
#define STATUS_NOT_EQUAL(_s, _o)                            \
    ({                                                      \
        bool __result;                                      \
        if (_o == RCO_LE || _o == RCO_EQ || _o == RCO_GE)   \
            __result = !_s;                                 \
        else                                                \
            __result = _s;                                  \
        __result;                                           \
    })


/* Détermine le type d'une interface pour un objet comparable. */
GType g_comparable_item_get_type(void) G_GNUC_CONST;

/* Réalise une comparaison entre objets selon un critère précis. */
bool g_comparable_item_compare_rich(const GComparableItem *, const GComparableItem *, RichCmpOperation, bool *);



#endif  /* _GLIBEXT_COMPARISON_H */
