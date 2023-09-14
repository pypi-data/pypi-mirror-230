
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bits.c - manipulation d'un champ de bits quelconque
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "bits.h"


#include <assert.h>
#include <glib.h>
#include <malloc.h>
#include <string.h>


#include "asm.h"



/* Champ de bits simple */
struct _bitfield_t
{
    size_t length;                          /* Nombre de bits représentés  */
    size_t requested;                       /* Nombre de mots alloués      */

    bool default_state;                     /* Etat d'initialisation       */

    unsigned long bits[0];                  /* Mémoire d'accès associée    */

};


/* Crée un champ de bits initialisé à zéro. */
static bitfield_t *_create_bit_field(size_t);

/* Détermine si un ensemble de bits est homogène dans un champ. */
static bool test_state_in_bit_field(const bitfield_t *, size_t, size_t, bool);

/* Teste l'état de bits selon un masque de bits. */
static bool test_state_within_bit_field(const bitfield_t *, size_t, const bitfield_t *, bool);



/******************************************************************************
*                                                                             *
*  Paramètres  : length = nom de bits du champ à représenter.                 *
*                                                                             *
*  Description : Crée un champ de bits initialisé à zéro.                     *
*                                                                             *
*  Retour      : Champ de bits mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bitfield_t *_create_bit_field(size_t length)
{
    bitfield_t *result;                     /* Création à retourner        */
    size_t requested;                       /* Nombre de mots à allouer    */
    size_t base;                            /* Allocation de base en octets*/

    requested = length / (sizeof(unsigned long) * 8);
    if (length % (sizeof(unsigned long) * 8) != 0) requested++;

    base = sizeof(bitfield_t) + requested * sizeof(unsigned long);

    result = (bitfield_t *)malloc(base);

    result->length = length;
    result->requested = requested;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : length = nombre de bits du champ à représenter.              *
*                state  = état initial de chaque des bits.                    *
*                                                                             *
*  Description : Crée un champ de bits initialisé.                            *
*                                                                             *
*  Retour      : Champ de bits mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bitfield_t *create_bit_field(size_t length, bool state)
{
    bitfield_t *result;                     /* Création à retourner        */

    result = _create_bit_field(length);

    result->default_state = state;

    if (state)
        set_all_in_bit_field(result);
    else
        reset_all_in_bit_field(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à dupliquer.                           *
*                                                                             *
*  Description : Crée une copie d'un champ de bits classique.                 *
*                                                                             *
*  Retour      : Champ de bits mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bitfield_t *dup_bit_field(const bitfield_t *field)
{
    bitfield_t *result;                     /* Copie à retourner           */

    result = _create_bit_field(field->length);

    memcpy(result->bits, field->bits, result->requested * sizeof(unsigned long));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à effacer.                             *
*                                                                             *
*  Description : Supprime de la mémoire un champ de bits donné.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_bit_field(bitfield_t *field)
{
    free(field);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = champ de bits à modifier.                             *
*                src  = champ de bits à utiliser pour l'opération.            *
*                                                                             *
*  Description : Copie un champ de bits dans un autre.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_bit_field(bitfield_t *dest, const bitfield_t *src)
{
    assert(dest->length == src->length);

    memcpy(dest->bits, src->bits, dest->requested * sizeof(unsigned long));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field  = champ de bits à modifier. [OUT]                     *
*                length = nouveau nombre de bits du champ à représenter.      *
*                                                                             *
*  Description : Redimensionne un champ de bits.                              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void resize_bit_field(bitfield_t **field, size_t length)
{
    bitfield_t *_field;                     /* Commodité d'accès           */
    size_t requested;                       /* Nombre de mots à allouer    */
    size_t base;                            /* Allocation de base en octets*/
    size_t remaining;                       /* Nombre de derniers bits     */
    size_t last;                            /* Dernier mot utilisé         */
    unsigned long mask;                     /* Masque d'initialisation     */
    size_t i;                               /* Boucle de parcours          */

    _field = *field;

    if (_field->length != length)
    {
        /* Redimensionnement */

        requested = length / (sizeof(unsigned long) * 8);
        if (length % (sizeof(unsigned long) * 8) != 0) requested++;

        base = sizeof(bitfield_t) + requested * sizeof(unsigned long);

        *field = realloc(_field, base);
        _field = *field;

        /* Initialisation, si nécessaire */

        if (_field->length < length)
        {
            last = _field->length / (sizeof(unsigned long) * 8);
            remaining = _field->length % (sizeof(unsigned long) * 8);

            if (remaining != 0)
            {
                mask = (1ul << remaining) - 1;

                if (_field->default_state)
                    _field->bits[last] |= ~mask;
                else
                    _field->bits[last] &= mask;

                last++;

            }

            for (i = last; i < requested; i++)
            {
                if (_field->default_state)
                    _field->bits[i] = ~0ul;
                else
                    _field->bits[i] = 0ul;
            }

        }

        /* Actualisation des tailles */

        _field->length = length;
        _field->requested = requested;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à consulter.                           *
*                                                                             *
*  Description : Indique la taille d'un champ de bits donné.                  *
*                                                                             *
*  Retour      : Taille du champ de bits.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t get_bit_field_size(const bitfield_t *field)
{
    size_t result;                          /* Dimension à retourner       */

    result = field->length;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier champ à analyser.                                *
*                b = second champ à analyser.                                 *
*                                                                             *
*  Description : Compare deux champs de bits entre eux.                       *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int compare_bit_fields(const bitfield_t *a, const bitfield_t *b)
{
    int result;                             /* Bilan à retourner           */
    unsigned long final;                    /* Masque de la partie finale  */
    size_t i;                               /* Boucle de parcours          */
    unsigned long val_a;                    /* Valeur d'un mot de A        */
    unsigned long val_b;                    /* Valeur d'un mot de B        */

    result = 0;

    if (a->length > b->length)
        result = 1;

    else if (a->length < b->length)
        result = -1;

    else
    {
        final = a->length % (8 * sizeof(unsigned long));

        if (final == 0)
            final = ~0lu;
        else
            final = (1 << final) - 1;

        for (i = 0; i < a->requested && result == 0; i++)
        {
            val_a = a->bits[i];
            val_b = b->bits[i];

            if ((i + 1) == a->requested)
            {
                val_a &= final;
                val_b &= final;
            }

            if (val_a > val_b)
                result = 1;

            else if (val_a < val_b)
                result = -1;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                                                                             *
*  Description : Bascule à 0 un champ de bits dans son intégralité.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_all_in_bit_field(bitfield_t *field)
{
    memset(field->bits, 0u, field->requested * sizeof(unsigned long));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                                                                             *
*  Description : Bascule à 1 un champ de bits dans son intégralité.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_all_in_bit_field(bitfield_t *field)
{
    memset(field->bits, ~0u, field->requested * sizeof(unsigned long));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                first = indice du premier bit à traiter.                     *
*                count = nombre de bits à marquer.                            *
*                                                                             *
*  Description : Bascule à 0 une partie d'un champ de bits.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_in_bit_field(bitfield_t *field, size_t first, size_t count)
{
    size_t last;                            /* Point d'arrêt de la boucle  */
    size_t i;                               /* Boucle de parcours          */
    size_t index;                           /* Cellule de tableau visée    */
    size_t remaining;                       /* Nombre de bits restants     */

    last = first + count;

    assert(last <= field->length);

    for (i = first; i < last; i++)
    {
        index = i / (sizeof(unsigned long) * 8);
        remaining = i % (sizeof(unsigned long) * 8);

        field->bits[index] &= ~(1ul << remaining);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                first = indice du premier bit à traiter.                     *
*                count = nombre de bits à marquer.                            *
*                                                                             *
*  Description : Bascule à 1 une partie d'un champ de bits.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_in_bit_field(bitfield_t *field, size_t first, size_t count)
{
    size_t last;                            /* Point d'arrêt de la boucle  */
    size_t i;                               /* Boucle de parcours          */
    size_t index;                           /* Cellule de tableau visée    */
    size_t remaining;                       /* Nombre de bits restants     */

    last = first + count;

    assert(last <= field->length);

    for (i = first; i < last; i++)
    {
        index = i / (sizeof(unsigned long) * 8);
        remaining = i % (sizeof(unsigned long) * 8);

        field->bits[index] |= (1ul << remaining);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = champ de bits à modifier.                             *
*                src  = champ de bits à utiliser pour l'opération.            *
*                                                                             *
*  Description : Réalise une opération ET logique entre deux champs de bits.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void and_bit_field(bitfield_t *dest, const bitfield_t *src)
{
    size_t i;                               /* Boucle de parcours          */

    assert(dest->length == src->length);

    for (i = 0; i < dest->requested; i++)
        dest->bits[i] &= src->bits[i];

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = champ de bits à modifier.                             *
*                src  = champ de bits à utiliser pour l'opération.            *
*                                                                             *
*  Description : Réalise une opération OU logique entre deux champs de bits.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void or_bit_field(bitfield_t *dest, const bitfield_t *src)
{
    size_t i;                               /* Boucle de parcours          */

    assert(dest->length == src->length);

    for (i = 0; i < dest->requested; i++)
        dest->bits[i] |= src->bits[i];

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest  = champ de bits à modifier.                            *
*                src   = champ de bits à utiliser pour l'opération.           *
*                first = point de départ pour l'opération à réaliser.         *
*                                                                             *
*  Description : Réalise une opération OU logique entre deux champs de bits.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void or_bit_field_at(bitfield_t *dest, const bitfield_t *src, size_t first)
{
    size_t start;                           /* Mot de départ dans le champ */
    size_t offset;                          /* Décalage des mots à basculer*/
    size_t remaining;                       /* Taille du dernier tronçon   */
    size_t last_iter;                       /* Dernière itération à mener  */
    size_t i;                               /* Boucle de parcours          */
    unsigned long word;                     /* Mot reconstituté à tester   */

    assert((first + src->length) <= dest->length);

    start = first / (sizeof(unsigned long) * 8);
    offset = first % (sizeof(unsigned long) * 8);

    remaining = (first + src->length) % (sizeof(unsigned long) * 8);

    if ((first + src->length) % (sizeof(unsigned long) * 8) > 0)
        last_iter = src->requested;
    else
        last_iter = src->requested - 1;


    for (i = 0; i <= last_iter; i++)
    {
        if (i < src->requested)
            word = src->bits[i] << offset;
        else
            word = 0;

        if (i > 0 && offset > 0)
            word |= src->bits[i - 1] >> (sizeof(unsigned long) * 8 - offset);

        if (i == last_iter && remaining > 0)
            word &= (1ul << remaining) - 1;

        dest->bits[start + i] |= word;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à consulter.                           *
*                n     = indice du bit à traiter.                             *
*                                                                             *
*  Description : Détermine si un bit est à 1 dans un champ de bits.           *
*                                                                             *
*  Retour      : true si le bit correspondant est à l'état haut.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool test_in_bit_field(const bitfield_t *field, size_t n)
{
    bool result;                            /* Valeur retrouvée à renvoyer */
    size_t index;                           /* Cellule de tableau visée    */
    size_t remaining;                       /* Nombre de bits restants     */

    assert(n < field->length);

    index = n / (sizeof(unsigned long) * 8);
    remaining = n % (sizeof(unsigned long) * 8);

    result = field->bits[index] & (1ul << remaining);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                first = indice du premier bit à traiter.                     *
*                count = nombre de bits à marquer.                            *
*                state = état global à retrouver idéalement.                  *
*                                                                             *
*  Description : Détermine si un ensemble de bits est homogène dans un champ. *
*                                                                             *
*  Retour      : true si les bits correspondants sont à l'état indiqué.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool test_state_in_bit_field(const bitfield_t *field, size_t first, size_t count, bool state)
{
    size_t last;                            /* Point d'arrêt de la boucle  */
    size_t i;                               /* Boucle de parcours          */
    size_t index;                           /* Cellule de tableau visée    */
    size_t remaining;                       /* Nombre de bits restants     */
    bool current;                           /* Etat d'un bit donné         */

    assert(count > 0);

    last = first + count;

    for (i = first; i < last; i++)
    {
        index = i / (sizeof(unsigned long) * 8);
        remaining = i % (sizeof(unsigned long) * 8);

        current = field->bits[index] & (1ul << remaining);

        if (current != state) break;

    }

    return (i == last);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à consulter.                           *
*                first = indice du premier bit à traiter.                     *
*                count = nombre de bits à analyser.                           *
*                                                                             *
*  Description : Détermine si un ensemble de bits est à 0 dans un champ.      *
*                                                                             *
*  Retour      : true si les bits correspondants sont à l'état bas.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool test_none_in_bit_field(const bitfield_t *field, size_t first, size_t count)
{
    bool result;                            /* Valeur retrouvée à renvoyer */

    result = test_state_in_bit_field(field, first, count, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à consulter.                           *
*                first = indice du premier bit à traiter.                     *
*                count = nombre de bits à analyser.                           *
*                                                                             *
*  Description : Détermine si un ensemble de bits est à 1 dans un champ.      *
*                                                                             *
*  Retour      : true si les bits correspondants sont à l'état haut.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool test_all_in_bit_field(const bitfield_t *field, size_t first, size_t count)
{
    bool result;                            /* Valeur retrouvée à renvoyer */

    result = test_state_in_bit_field(field, first, count, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                first = indice du premier bit à traiter.                     *
*                mask  = second champ de bits à tester logiquement.           *
*                state = état global à retrouver idéalement.                  *
*                                                                             *
*  Description : Teste l'état de bits selon un masque de bits.                *
*                                                                             *
*  Retour      : true si les bits visés sont tous à l'état indiqué.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool test_state_within_bit_field(const bitfield_t *field, size_t first, const bitfield_t *mask, bool state)
{
    bool result;                            /* Bilan à retourner           */
    size_t start;                           /* Mot de départ dans le champ */
    size_t offset;                          /* Décalage des mots à testter */
    size_t remaining;                       /* Taille du dernier tronçon   */
    unsigned long finalcut;                 /* Limitation du mot final     */
    size_t i;                               /* Boucle de parcours          */
    size_t windex;                          /* Indice du mot courant       */
    unsigned long word;                     /* Mot reconstituté à tester   */
    unsigned long bitmask;                  /* Masque à appliquer          */
    unsigned long test;                     /* Valeur résultante du test   */

    result = true;

    assert((first + mask->length) <= field->length);

    start = first / (sizeof(unsigned long) * 8);
    offset = first % (sizeof(unsigned long) * 8);

    remaining = mask->length % (sizeof(unsigned long) * 8);

    if (remaining == 0)
        finalcut = ~0lu;
    else
        finalcut = (1lu << remaining) - 1;

    for (i = 0; i < mask->requested && result; i++)
    {
        windex = start + i;

        if (offset == 0)
            word = field->bits[windex];

        else
        {
            word = field->bits[windex] >> offset;
            if ((windex + 1) < field->requested)
                word |= field->bits[windex + 1] << (sizeof(unsigned long) * 8 - offset);
        }

        bitmask = mask->bits[i];

        test = word ^ bitmask;

        test &= bitmask;

        if ((i + 1) == mask->requested)
        {
            bitmask &= finalcut;
            test &= finalcut;
        }

        result = (state ? test == 0 : test == bitmask);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                first = indice du premier bit à traiter.                     *
*                mask  = second champ de bits à tester logiquement.           *
*                                                                             *
*  Description : Teste l'état à 0 de bits selon un masque de bits.            *
*                                                                             *
*  Retour      : true si les bits visés sont à l'état bas.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool test_zeros_within_bit_field(const bitfield_t *field, size_t first, const bitfield_t *mask)
{
    bool result;                            /* Valeur retrouvée à renvoyer */

    result = test_state_within_bit_field(field, first, mask, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à modifier.                            *
*                first = indice du premier bit à traiter.                     *
*                mask  = second champ de bits à tester logiquement.           *
*                                                                             *
*  Description : Teste l'état à 1 de bits selon un masque de bits.            *
*                                                                             *
*  Retour      : true si les bits visés sont à l'état haut.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool test_ones_within_bit_field(const bitfield_t *field, size_t first, const bitfield_t *mask)
{
    bool result;                            /* Valeur retrouvée à renvoyer */

    result = test_state_within_bit_field(field, first, mask, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à consulter.                           *
*                                                                             *
*  Description : Détermine le nombre de bits à 1 dans un champ.               *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t popcount_for_bit_field(const bitfield_t *field)
{
    size_t result;                          /* Quantité à renvoyer         */
    size_t remaining;                       /* Nombre de bits restants     */
    size_t i;                               /* Boucle de parcours          */
    unsigned long value;                    /* Valeur masquée à traiter    */

    result = 0;

    remaining = field->length;

    for (i = 0; i < field->requested; i++)
    {
        value = field->bits[i];

        if (remaining < (8 * sizeof(unsigned long)))
            value &= (1lu << remaining) - 1;

#if __WORDSIZE == 64
        result += popcount_64(value);
#elif __WORDSIZE == 32
        result += popcount_32(value);
#else
#   error "Unkown word size"
#endif

        remaining -= 8 * sizeof(unsigned long);

    }

    return result;

}
