
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sort.c - opérations sur des tableaux triés
 *
 * Copyright (C) 2016-2020 Cyrille Bagard
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


#include "sort.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à consulter et comparer.                 *
*                b = second élément à consulter et comparer.                  *
*                                                                             *
*  Description : Compare un booléen avec une autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int sort_boolean(bool a, bool b)
{
    int result;                             /* Bilan à renvoyer            */

    if (a && !b)
        result = 1;

    else if (!a && b)
        result = -1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à consulter et comparer.                 *
*                b = second élément à consulter et comparer.                  *
*                                                                             *
*  Description : Compare une valeur avec une autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int sort_unsigned_long(unsigned long a, unsigned long b)
{
    int result;                             /* Bilan à renvoyer            */

    if (a < b)
        result = -1;

    else if (a > b)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à consulter et comparer.                 *
*                b = second élément à consulter et comparer.                  *
*                                                                             *
*  Description : Compare une valeur avec une autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int sort_signed_long_long(signed long long a, signed long long b)
{
    int result;                             /* Bilan à renvoyer            */

    if (a < b)
        result = -1;

    else if (a > b)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à consulter et comparer.                 *
*                b = second élément à consulter et comparer.                  *
*                                                                             *
*  Description : Compare une valeur avec une autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int sort_unsigned_long_long(unsigned long long a, unsigned long long b)
{
    int result;                             /* Bilan à renvoyer            */

    if (a < b)
        result = -1;

    else if (a > b)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à consulter et comparer.                 *
*                b = second élément à consulter et comparer.                  *
*                                                                             *
*  Description : Compare une valeur de 64 bits avec une autre.                *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int sort_uint64_t(uint64_t a, uint64_t b)
{
    int result;                             /* Bilan à renvoyer            */

    if (a < b)
        result = -1;

    else if (a > b)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a      = premier élément à consulter et comparer.            *
*                b      = second élément à consulter et comparer.             *
*                compar = méthode de comparaison entre éléments.              *
*                                                                             *
*  Description : Compare un pointeur avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int sort_pointer(const void *a, const void *b, __compar_fn_t compar)
{
    int result;                             /* Bilan à renvoyer            */

    if (a != NULL && b == NULL)
        result = 1;

    else if (a == NULL && b != NULL)
        result = -1;

    else if (a == NULL && b == NULL)
        result = 0;

    else
        result = compar(a, b);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key    = élément de comparaison à retrouver ou approcher.    *
*                base   = adresse du tableau à parcourir.                     *
*                nmemb  = nombre d'éléments présents au total.                *
*                size   = taille de chaque élément du tableau.                *
*                compar = méthode de comparaison entre éléments.              *
*                index  = indice de cellule d'insertion.                      *
*                                                                             *
*  Description : Effectue une recherche dichotomique dans un tableau.         *
*                                                                             *
*  Retour      : true si l'élément visé à été trouvé, false sinon.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool bsearch_index(const void *key, const void *base, size_t nmemb, size_t size, __compar_fn_t compar, size_t *index)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t lower;                           /* Borne inférieure de fenêtre */
    size_t upper;                           /* Borne supérieure qde fenêtre*/
    size_t idx;                             /* Indice de cellule analysée  */
    const void *cell;                       /* Cellule en question         */
    int status;                             /* Bilan d'une comparaison     */

    if (nmemb == 0)
    {
        *index = 0;
        return false;
    }

    /* Parcours minimal */

    lower = 0;
    upper = nmemb;

    while (lower < upper)
    {
        idx = (lower + upper) / 2;
        cell = (void *)(((const char *)base) + (idx * size));

        status = (*compar)(key, cell);

        if (status < 0)
            upper = idx;

        else if (status > 0)
            lower = idx + 1;

        else
            break;

    }

    /* Bilan des recherches */

    result = (status == 0);

    if (status < 0)
        *index = idx;

    else if (status > 0)
        *index = idx + 1;

    else
        *index = idx;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base  = adresse du tableau à parcourir.                      *
*                nmemb = nombre d'éléments présents au total. [OUT]           *
*                size  = taille de chaque élément du tableau.                 *
*                new   = nouvel élément à insérer.                            *
*                index = indice du point d'insertion.                         *
*                                                                             *
*  Description : Ajoute à l'endroit indiqué un élément dans un tableau.       *
*                                                                             *
*  Retour      : Nouvel emplacement du tableau agrandi.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *_qinsert(void *base, size_t *nmemb, size_t size, void *new, size_t index)
{
    void *result;                           /* Tableau trié à retourner    */

    result = realloc(base, (*nmemb + 1) * size);

    if (index < *nmemb)
        memmove((char *)result + (index + 1) * size, (char *)result + index * size, (*nmemb - index) * size);

    (*nmemb)++;

    memcpy((char *)result + index * size, new, size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base  = adresse du tableau à parcourir.                      *
*                nmemb = nombre d'éléments présents au total. [OUT]           *
*                size  = taille de chaque élément du tableau.                 *
*                new   = nouveaux éléments à insérer.                         *
*                count = quantité de ces nouveaux éléments.                   *
*                index = indice du point d'insertion.                         *
*                                                                             *
*  Description : Ajoute à l'endroit indiqué des éléments dans un tableau.     *
*                                                                             *
*  Retour      : Nouvel emplacement du tableau agrandi.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *_qinsert_batch(void *base, size_t *nmemb, size_t size, void *new, size_t count, size_t index)
{
    void *result;                           /* Tableau trié à retourner    */

    result = realloc(base, (*nmemb + count) * size);

    if (index < *nmemb)
        memmove((char *)result + (index + count) * size, (char *)result + index * size, (*nmemb - index) * size);

    (*nmemb) += count;

    memcpy((char *)result + index * size, new, count * size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base   = adresse du tableau à parcourir.                     *
*                nmemb  = nombre d'éléments présents au total. [OUT]          *
*                size   = taille de chaque élément du tableau.                *
*                compar = méthode de comparaison entre éléments.              *
*                new    = nouvel élément à insérer.                           *
*                                                                             *
*  Description : Ajoute au bon endroit un élément dans un tableau trié.       *
*                                                                             *
*  Retour      : Nouvel emplacement du tableau agrandi.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *qinsert(void *base, size_t *nmemb, size_t size, __compar_fn_t compar, void *new)
{
    void *result;                           /* Tableau trié à retourner    */
#ifndef NDEBUG
    bool found;                             /* Présence de partage existant*/
#endif
    size_t index;                           /* Indice du point d'insertion */

#ifndef NDEBUG
    found = bsearch_index(new, base, *nmemb, size, compar, &index);
    assert(!found);
#else
    bsearch_index(new, base, *nmemb, size, compar, &index);
#endif

    result = _qinsert(base, nmemb, size, new, index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base   = adresse du tableau à parcourir.                     *
*                nmemb  = nombre d'éléments présents au total. [OUT]          *
*                size   = taille de chaque élément du tableau.                *
*                compar = méthode de comparaison entre éléments.              *
*                new    = nouvel élément à insérer.                           *
*                                                                             *
*  Description : Ajoute au bon endroit un élément dans un tableau trié.       *
*                                                                             *
*  Retour      : Nouvel emplacement du tableau agrandi.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *qinsert_multi(void *base, size_t *nmemb, size_t size, __compar_fn_t compar, void *new)
{
    void *result;                           /* Tableau trié à retourner    */
    size_t index;                           /* Indice du point d'insertion */

    bsearch_index(new, base, *nmemb, size, compar, &index);

    result = _qinsert(base, nmemb, size, new, index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base  = adresse du tableau à parcourir.                      *
*                nmem  = nombre d'éléments présents au total. [OUT]           *
*                size  = taille de chaque élément du tableau.                 *
*                inde  = indice du point de suppression.                      *
*                                                                             *
*  Description : Supprime un élément dans un tableau trié.                    *
*                                                                             *
*  Retour      : Nouvel emplacement du tableau rétréci.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *_qdelete(void *base, size_t *nmemb, size_t size, size_t index)
{
    void *result;                           /* Tableau trié à retourner    */

    if ((index + 1) < *nmemb)
        memmove((char *)base + index * size, (char *)base + (index + 1) * size, (*nmemb - index - 1) * size);

    (*nmemb)--;

    result = realloc(base, *nmemb * size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base   = adresse du tableau à parcourir.                     *
*                nmemb  = nombre d'éléments présents au total. [OUT]          *
*                size   = taille de chaque élément du tableau.                *
*                compar = méthode de comparaison entre éléments.              *
*                target = élément en place à retirer.                         *
*                                                                             *
*  Description : Supprime un élément dans un tableau trié.                    *
*                                                                             *
*  Retour      : Nouvel emplacement du tableau rétréci.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *qdelete(void *base, size_t *nmemb, size_t size, __compar_fn_t compar, void *target)
{
    void *result;                           /* Tableau trié à retourner    */
#ifndef NDEBUG
    bool found;                             /* Présence de partage existant*/
#endif
    size_t index;                           /* Indice du point d'insertion */

#ifndef NDEBUG
    found = bsearch_index(target, base, *nmemb, size, compar, &index);
    assert(found);
#else
    bsearch_index(target, base, *nmemb, size, compar, &index);
#endif

    result = _qdelete(base, nmemb, size, index);

    return result;

}
