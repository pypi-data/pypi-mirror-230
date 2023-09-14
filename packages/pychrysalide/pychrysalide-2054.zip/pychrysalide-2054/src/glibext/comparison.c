
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comparison.c - opérations de comparaison d'objets
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


#include "comparison.h"


#include <assert.h>


#include "comparison-int.h"



/* Procède à l'initialisation de l'interface de comparaison. */
static void g_comparable_item_default_init(GComparableItemInterface *);



/* Détermine le type d'une interface pour un objet comparable. */
G_DEFINE_INTERFACE(GComparableItem, g_comparable_item, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de comparaison.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_comparable_item_default_init(GComparableItemInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = premier objet à consulter pour une comparaison.     *
*                other  = second objet à consulter pour une comparaison.      *
*                op     = opération de comparaison à réaliser.                *
*                status = bilan des opérations de comparaison. [OUT]          *
*                                                                             *
*  Description : Réalise une comparaison entre objets selon un critère précis.*
*                                                                             *
*  Retour      : true si la comparaison a pu être effectuée, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_comparable_item_compare_rich(const GComparableItem *item, const GComparableItem *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */
    GComparableItemIface *iface;            /* Interface utilisée          */

    iface = G_COMPARABLE_ITEM_GET_IFACE(item);

    result = iface->cmp_rich(item, other, op, status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier élément à consulter pour une comparaison.       *
*                b  = second objet à consulter pour une comparaison.          *
*                op = opération de comparaison à réaliser.                    *
*                                                                             *
*  Description : Réalise une comparaison riche entre valeurs entière.         *
*                                                                             *
*  Retour      : Bilan des opérations de comparaison.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool compare_rich_integer_values_signed(long long a, long long b, RichCmpOperation op)
{
    bool result;                            /* Bilan  à retourner          */

    switch (op)
    {
        case RCO_LT:
            result = (a < b);
            break;

        case RCO_LE:
            result = (a <= b);
            break;

        case RCO_EQ:
            result = (a == b);
            break;

        case RCO_NE:
            result = (a != b);
            break;

        case RCO_GT:
            result = (a > b);
            break;

        case RCO_GE:
            result = (a >= b);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier élément à consulter pour une comparaison.       *
*                b  = second objet à consulter pour une comparaison.          *
*                op = opération de comparaison à réaliser.                    *
*                                                                             *
*  Description : Réalise une comparaison riche entre valeurs entière.         *
*                                                                             *
*  Retour      : Bilan des opérations de comparaison.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool compare_rich_integer_values_unsigned(unsigned long long a, unsigned long long b, RichCmpOperation op)
{
    bool result;                            /* Bilan  à retourner          */

    switch (op)
    {
        case RCO_LT:
            result = (a < b);
            break;

        case RCO_LE:
            result = (a <= b);
            break;

        case RCO_EQ:
            result = (a == b);
            break;

        case RCO_NE:
            result = (a != b);
            break;

        case RCO_GT:
            result = (a > b);
            break;

        case RCO_GE:
            result = (a >= b);
            break;

        default:
            assert(false);
            result = false;
            break;

    }

    return result;

}
