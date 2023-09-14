
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symiter.c - prototypes pour le parcours simplifié d'un ensemble de symboles
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "symiter.h"


#include <malloc.h>


#include "format.h"



/* Suivi d'un parcours de symboles */
typedef struct _sym_iter_t
{
    GBinFormat *format;                     /* Conteneur associé           */
    unsigned int stamp;                     /* Suivi d'évolutions externes */

    size_t index;                           /* Symbole courant             */

    mrange_t restriction;                   /* Enventuelle limite de zone  */
    bool is_restricted;                     /* Validité de l'étendue       */

} sym_iter_t;



/******************************************************************************
*                                                                             *
*  Paramètres  : format = processeur recensant divers symboles.               *
*                index  = indice du premier symbole à fournir.                *
*                                                                             *
*  Description : Construit un itérateur pour parcourir des symboles.          *
*                                                                             *
*  Retour      : Itérateur prêt à emploi.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

sym_iter_t *create_symbol_iterator(GBinFormat *format, size_t index)
{
    sym_iter_t *result;                     /* Structure à retourner       */

#ifndef NDEBUG
    if (index > 0)
        g_binary_format_check_for_symbols_lock(format);
#endif

    result = (sym_iter_t *)malloc(sizeof(sym_iter_t));

    g_object_ref(G_OBJECT(format));

    result->format = format;
    result->stamp = g_binary_format_get_symbols_stamp(format);

    result->index = index;

    result->is_restricted = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à traiter.                                  *
*                                                                             *
*  Description : Détruit un itérateur mis en place.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_symbol_iterator(sym_iter_t *iter)
{
    g_object_unref(G_OBJECT(iter->format));

    free(iter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter  = itérateur à traiter.                                 *
*                range = bornes de l'espace de parcours.                      *
*                                                                             *
*  Description : Limite le parcours des symboles à une zone donnée.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void restrict_symbol_iterator(sym_iter_t *iter, const mrange_t *range)
{
    copy_mrange(&iter->restriction, range);

    iter->is_restricted = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit le symbole courant de l'itérateur.                   *
*                                                                             *
*  Retour      : Symbole suivant trouvé, ou NULL.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *get_symbol_iterator_current(sym_iter_t *iter)
{
    GBinSymbol *result;                     /* Résultat à retourner        */
    const mrange_t *irange;                 /* Emplacement de symbole      */

    g_binary_format_lock_symbols_rd(iter->format);

    if (iter->stamp != g_binary_format_get_symbols_stamp(iter->format))
        result = NULL;

    else
    {
        if (iter->index < g_binary_format_count_symbols(iter->format))
        {
            result = g_binary_format_get_symbol(iter->format, iter->index);

            /* Le symbole sort-il des clous ? */
            if (iter->is_restricted)
            {
                irange = g_binary_symbol_get_range(result);

                if (!mrange_contains_mrange(&iter->restriction, irange))
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

        }

        else
            result = NULL;

    }

    g_binary_format_unlock_symbols_rd(iter->format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit le symbole qui en précède un autre.                  *
*                                                                             *
*  Retour      : Symbole suivant trouvé, ou NULL.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *get_symbol_iterator_prev(sym_iter_t *iter)
{
    GBinSymbol *result;                     /* Résultat à retourner        */
    const mrange_t *irange;                 /* Emplacement de symbole      */

    g_binary_format_lock_symbols_rd(iter->format);

    if (iter->stamp != g_binary_format_get_symbols_stamp(iter->format))
        result = NULL;

    else
    {
        if (iter->index > 1)
        {
            iter->index--;
            result = g_binary_format_get_symbol(iter->format, iter->index);

            /* Le symbole sort-il des clous ? */
            if (iter->is_restricted)
            {
                irange = g_binary_symbol_get_range(result);

                if (!mrange_contains_mrange(&iter->restriction, irange))
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

        }

        else
            result = NULL;

    }

    g_binary_format_unlock_symbols_rd(iter->format);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit le symbole qui en suit un autre.                     *
*                                                                             *
*  Retour      : Symbole suivant trouvé, ou NULL.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *get_symbol_iterator_next(sym_iter_t *iter)
{
    GBinSymbol *result;                     /* Résultat à retourner        */
    const mrange_t *irange;                 /* Emplacement de symbole      */

    g_binary_format_lock_symbols_rd(iter->format);

    if (iter->stamp != g_binary_format_get_symbols_stamp(iter->format))
        result = NULL;

    else
    {
        if ((iter->index + 1) < g_binary_format_count_symbols(iter->format))
        {
            iter->index++;
            result = g_binary_format_get_symbol(iter->format, iter->index);

            /* Le symbole sort-il des clous ? */
            if (iter->is_restricted)
            {
                irange = g_binary_symbol_get_range(result);

                if (!mrange_contains_mrange(&iter->restriction, irange))
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

        }

        else
            result = NULL;

    }

    g_binary_format_unlock_symbols_rd(iter->format);

    return result;

}
