
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comparison-int.h - définitions internes propres aux opérations de comparaison d'objets
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GLIBEXT_COMPARISON_INT_H
#define _GLIBEXT_COMPARISON_INT_H


#include "comparison.h"



/* Réalise une comparaison entre objets selon un critère précis. */
typedef bool (* compare_rich_fc) (const GComparableItem *, const GComparableItem *, RichCmpOperation, bool *);


/* Instance d'élément comparable (interface) */
struct _GComparableItemIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    compare_rich_fc cmp_rich;               /* Comparaison de façon précise*/

};


/* Redéfinition */
typedef GComparableItemIface GComparableItemInterface;


/* Réalise une comparaison riche entre valeurs entière. */
bool compare_rich_integer_values_signed(long long, long long, RichCmpOperation);

/* Réalise une comparaison riche entre valeurs entière. */
bool compare_rich_integer_values_unsigned(unsigned long long, unsigned long long, RichCmpOperation);



#endif  /* _GLIBEXT_COMPARISON_INT_H */
