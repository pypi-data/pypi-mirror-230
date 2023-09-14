
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.c - manipulation optimisée de tableaux au niveau de l'empreinte mémoire
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "array.h"


#include <assert.h>
#include <endian.h>
#include <glib.h>
#include <malloc.h>
#include <string.h>


#include "sort.h"



/**
 * L'expression du besoin d'une gestion optimisée des tableaux se base sur la
 * structure usuelle et naïve suivante :
 *
 *    {
 *        void **array;
 *        size_t count;
 *    }
 *
 * Déjà, size_t mesure la taille d'un long sur 64 bits. Ensuite, si le tableau
 * renvoie effectivement vers des pointeurs, un tableau à un seul élément va
 * allouer 8 octets (sur 64 bits) pour stocker ce seul élément. Cela fait donc
 * 16 octets inutiles.
 *
 * Le jeu des alignements fait que la structure définie ici devrait être alignée
 * sur 8 octets.
 *
 * Cela laisse donc 3 bits toujours nuls à disposition pour conserver quelques
 * informations utiles.
 *
 * Cf. http://www.catb.org/esr/structure-packing/
 *
 * Pour les notions de verrouillage, la consommation mémoire peut vite augmenter :
 * GRWLock pèse par exemple 16 octets pour offrir la distinction entre consultation
 * et modification.
 *
 * Dans le même temps, des solutions plus légères existent : la GLib propose
 * incidemment les fonctions portables g_bit_lock() / g_bit_unlock().
 *
 * Cependant, elles ne fonctionnent que sur des gint. Donc il faut s'adapter pour
 * les architectures en grand boutisme. Comment il est peu vraisemblable que le
 * bit de poids fort habituellement associé à l'espace noyau se retrouve dans des
 * adresses utilisateurs manipulées ici, on l'utilise pour le verrou au besoin.
 */

#if __BYTE_ORDER == __LITTLE_ENDIAN

#   define FLAT_ARRAY_LOCK_BIT 0
#   define FLAT_ARRAY_LOCK_MASK (1 << 0)

#elif __BYTE_ORDER == __BIG_ENDIAN

#   define FLAT_ARRAY_LOCK_BIT 31
#   define FLAT_ARRAY_LOCK_MASK (1 << (__WORDSIZE - 1))

#else

#   error "Unknown byte order"

#endif

#define FLAT_ARRAY_INDEX_MASK (1 << 1)

#define FLAT_ARRAY_USED_MASK (FLAT_ARRAY_INDEX_MASK | FLAT_ARRAY_LOCK_MASK)


/* Tableau compressé à 2 éléments ou plus */
typedef struct _ext_flat_array_t
{
    void *items;                            /* Tableau d'éléments          */
    size_t count;                           /* Quantité d'éléments         */

} ext_flat_array_t;


#define FLAT_ARRAY_IS_LOCKED(a) (((unsigned long)a) & FLAT_ARRAY_LOCK_MASK)

#define FLAT_ARRAY_IS_EMPTY(a) ((((unsigned long)a) & ~FLAT_ARRAY_USED_MASK) == 0)

#define FLAT_ARRAY_HAS_NO_INDEX(a) ((((unsigned long)a) & FLAT_ARRAY_INDEX_MASK) == 0)

#define FLAT_ARRAY_SET_INDEX(a) *((unsigned long *)&a) |= FLAT_ARRAY_INDEX_MASK

#define GET_LONELY_ITEM(a) (void *)(((unsigned long)a) & ~FLAT_ARRAY_USED_MASK)

#define EXTENDED_ARRAY(a) (ext_flat_array_t *)(((unsigned long)a) & ~FLAT_ARRAY_USED_MASK)



/* Verrouille l'accès à une nouvelle adresse d'un tableau. */
static void relock_flat_array(flat_array_t **, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à modifier. [OUT]                  *
*                                                                             *
*  Description : Verrouille l'accès à un tableau compressé.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void lock_flat_array(flat_array_t **array)
{
    g_pointer_bit_lock(array, FLAT_ARRAY_LOCK_BIT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à modifier. [OUT]                  *
*                new   = nouvelle adresse à traiter atomiquement.             *
*                                                                             *
*  Description : Verrouille l'accès à une nouvelle adresse d'un tableau.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void relock_flat_array(flat_array_t **array, void *new)
{
    g_pointer_bit_lock(&new, FLAT_ARRAY_LOCK_BIT);

    g_atomic_pointer_set(array, new);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à modifier. [OUT]                  *
*                                                                             *
*  Description : Déverrouille l'accès à un tableau compressé.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unlock_flat_array(flat_array_t **array)
{
    g_pointer_bit_unlock(array, FLAT_ARRAY_LOCK_BIT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à mettre à jour. [OUT]             *
*                                                                             *
*  Description : Réinitialise un tableau sans traitement excessif.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_flat_array(flat_array_t **array)
{
    size_t count;                           /* Nombre d'éléments présents  */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */

    assert(FLAT_ARRAY_IS_LOCKED(*array));

    count = count_flat_array_items(*array);

    switch (count)
    {
        case 0:
            break;

        case 1:

            assert(FLAT_ARRAY_HAS_NO_INDEX(*array));

            free(GET_LONELY_ITEM(*array));

            relock_flat_array(array, NULL);

            break;

        default:

            assert(!FLAT_ARRAY_HAS_NO_INDEX(*array));

            extended = EXTENDED_ARRAY(*array);

            free(extended->items);
            free(extended);

            relock_flat_array(array, NULL);

            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : src    = tableau compressé à consulter.                      *
*                dest   = tableau compressé à constituer. [OUT]               *
*                size   = taille de ce nouvel élément.                        *
*                notify = éventuelle fonction à appeler sur chaque élément.   *
*                                                                             *
*  Description : Copie le contenu d'un tableau d'éléments dans un autre.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_flat_array_items(flat_array_t **src, flat_array_t **dest, size_t size, item_notify_cb notify)
{
    void *item;                             /* Elément manipulé            */
    void *new_single;                       /* Nouvelle copie crée         */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */
    ext_flat_array_t *new_ext;              /* Nouvelle copie créée        */
    size_t i;                               /* Boucle de parcours          */

    assert(!FLAT_ARRAY_IS_LOCKED(*src));
    assert(!FLAT_ARRAY_IS_LOCKED(*dest));

    lock_flat_array(src);
    lock_flat_array(dest);

    assert(FLAT_ARRAY_IS_EMPTY(*dest));

    if (FLAT_ARRAY_IS_EMPTY(*src))
        goto cfai_done;

    if (FLAT_ARRAY_HAS_NO_INDEX(*src))
    {
        item = GET_LONELY_ITEM(*src);

        if (notify != NULL)
            notify(item);

        new_single = malloc(size);
        memcpy(new_single, item, size);

        relock_flat_array(dest, new_single);

    }

    else
    {
        extended = EXTENDED_ARRAY(*src);

        new_ext = malloc(sizeof(ext_flat_array_t));

        new_ext->items = malloc(extended->count * size);
        new_ext->count = extended->count;

        memcpy(new_ext->items, extended->items, new_ext->count * size);

        if (notify != NULL)
            for (i = 0; i < new_ext->count; i++)
            {
                item = (void *)(((char *)new_ext->items) + i * size);
                notify(item);
            }

        FLAT_ARRAY_SET_INDEX(new_ext);

        relock_flat_array(dest, new_ext);

    }

 cfai_done:

    unlock_flat_array(src);
    unlock_flat_array(dest);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à consulter.                       *
*                                                                             *
*  Description : Indique la quantité d'éléments présents dans le tableau.     *
*                                                                             *
*  Retour      : Nombre d'éléments attachés.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t count_flat_array_items(const flat_array_t *array)
{
    size_t result;                          /* Quantité à retourner        */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */

    assert(FLAT_ARRAY_IS_LOCKED(array));

    if (FLAT_ARRAY_IS_EMPTY(array))
        result = 0;

    else
    {
        if (FLAT_ARRAY_HAS_NO_INDEX(array))
            result = 1;

        else
        {
            extended = EXTENDED_ARRAY(array);
            result = extended->count;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à mettre à jour. [OUT]             *
*                item  = adresse de l'élément à rajouter.                     *
*                size  = taille de ce nouvel élément.                         *
*                                                                             *
*  Description : Ajoute un élément supplémentaire à un tableau.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_item_to_flat_array(flat_array_t **array, const void *item, size_t size)
{
    void *single;                           /* Copie à un seul élément     */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */

    assert(FLAT_ARRAY_IS_LOCKED(*array));

    if (FLAT_ARRAY_IS_EMPTY(*array))
    {
        single = malloc(size);
        memcpy(single, item, size);

        relock_flat_array(array, single);

    }

    else
    {
        if (FLAT_ARRAY_HAS_NO_INDEX(*array))
        {
            extended = malloc(sizeof(ext_flat_array_t));

            extended->items = malloc(2 * size);
            extended->count = 2;

            single = GET_LONELY_ITEM(*array);

            memcpy(extended->items, single, size);
            memcpy(((char *)extended->items) + size, item, size);

            free(single);

            FLAT_ARRAY_SET_INDEX(extended);

            relock_flat_array(array, extended);

        }

        else
        {
            extended = EXTENDED_ARRAY(*array);

            extended->count++;
            extended->items = realloc(extended->items, extended->count * size);

            memcpy(((char *)extended->items) + (extended->count - 1) * size, item, size);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array  = tableau compressé à mettre à jour. [OUT]            *
*                item   = adresse de l'élément à rajouter.                    *
*                size   = taille de ce nouvel élément.                        *
*                compar = méthode de comparaison entre éléments.              *
*                                                                             *
*  Description : Ajoute un élément supplémentaire à un tableau trié.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void insert_item_into_flat_array(flat_array_t **array, void *item, size_t size, __compar_fn_t compar)
{
    void *single;                           /* Copie à un seul élément     */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */

    assert(FLAT_ARRAY_IS_LOCKED(*array));

    if (FLAT_ARRAY_IS_EMPTY(*array))
    {
        single = malloc(size);
        memcpy(single, item, size);

        relock_flat_array(array, single);

    }

    else
    {
        if (FLAT_ARRAY_HAS_NO_INDEX(*array))
        {
            extended = malloc(sizeof(ext_flat_array_t));

            extended->items = malloc(size);
            extended->count = 1;

            single = GET_LONELY_ITEM(*array);

            memcpy(extended->items, single, size);

            free(single);

            FLAT_ARRAY_SET_INDEX(extended);

            relock_flat_array(array, extended);

        }

        extended = EXTENDED_ARRAY(*array);

        extended->items = qinsert(extended->items, &extended->count, size, compar, item);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à mettre à jour.                   *
*                index = indice de l'élément à remplacer.                     *
*                new   = adresse de l'élément à rajouter.                     *
*                size  = taille de ce nouvel élément.                         *
*                                                                             *
*  Description : Remplace un élément d'un tableau compressé par un autre.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rpl_item_in_flat_array(flat_array_t *array, size_t index, void *new, size_t size)
{
    ext_flat_array_t *extended;             /* Version de tableau étendue  */

    assert(FLAT_ARRAY_IS_LOCKED(array));

    assert(!FLAT_ARRAY_IS_EMPTY(array));

    if (FLAT_ARRAY_HAS_NO_INDEX(array))
    {
        assert(index == 0);

        memcpy(GET_LONELY_ITEM(array), new, size);

    }

    else
    {
        extended = EXTENDED_ARRAY(array);

        assert(index < extended->count);

        memcpy(((char *)extended->items) + index * size, new, size);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à mettre à jour. [OUT]             *
*                index = indice de l'élément à retirer.                       *
*                size  = taille de ce nouvel élément.                         *
*                                                                             *
*  Description : Retire un élément existant d'un tableau.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rem_item_from_flat_array(flat_array_t **array, size_t index, size_t size)
{
    size_t count;                           /* Nombre d'éléments présents  */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */
    void *new;                              /* Nouveau tableau à jour      */

    assert(FLAT_ARRAY_IS_LOCKED(*array));

    count = count_flat_array_items(*array);

    switch (count)
    {
        case 0:
            assert(false);
            break;

        case 1:

            assert(FLAT_ARRAY_HAS_NO_INDEX(*array));
            assert(index == 0);

            free(GET_LONELY_ITEM(*array));

            relock_flat_array(array, NULL);

            break;

        case 2:

            assert(!FLAT_ARRAY_HAS_NO_INDEX(*array));
            assert(index == 0 || index == 1);

            extended = EXTENDED_ARRAY(*array);

            new = malloc(size);

            if (index == 1)
                memcpy(new, extended->items, size);
            else
                memcpy(new, ((char *)extended->items) + size, size);

            free(extended->items);
            free(extended);

            relock_flat_array(array, new);

            break;

        default:

            assert(!FLAT_ARRAY_HAS_NO_INDEX(*array));
            assert(index < count);

            extended = EXTENDED_ARRAY(*array);

            if ((count - index - 1) > 0)
                memmove(((char *)extended->items) + index * size,
                        ((char *)extended->items) + (index + 1) * size,
                        (count - index - 1) * size);

            extended->count--;
            extended->items = realloc(extended->items, extended->count * size);

            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array = tableau compressé à consulter.                       *
*                index = indice de l'élément à retrouver                      *
*                size  = taille de ce nouvel élément.                         *
*                                                                             *
*  Description : Fournit un élément présent dans un tableau compressé.        *
*                                                                             *
*  Retour      : Elément du tableau visé par la procédure.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *get_flat_array_item(flat_array_t *array, size_t index, size_t size)
{
    void *result;                           /* Trouvaille à retourner      */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */

    assert(FLAT_ARRAY_IS_LOCKED(array));

    assert(!FLAT_ARRAY_IS_EMPTY(array));

    if (FLAT_ARRAY_HAS_NO_INDEX(array))
    {
        assert(index == 0);

        result = GET_LONELY_ITEM(array);

    }

    else
    {
        extended = EXTENDED_ARRAY(array);

        assert(index < extended->count);

        result = (void *)(((char *)extended->items) + index * size);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : array  = tableau compressé à consulter.                      *
*                size   = taille de ce nouvel élément.                        *
*                compar = méthode de comparaison entre éléments.              *
*                key    = élément de comparaison fourni.                      *
*                                                                             *
*  Description : Recherche un élément dans un tableau trié.                   *
*                                                                             *
*  Retour      : Eventuel élément trouvé ou NULL.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *find_item_in_flat_array(flat_array_t *array, size_t size, __compar_fn_t compar, const void *key)
{
    void *result;                           /* Trouvaille à retourner      */
    size_t count;                           /* Nombre d'éléments présents  */
    void *item;                             /* Elément isolé présent       */
    ext_flat_array_t *extended;             /* Version de tableau étendue  */
    size_t index;                           /* Indice de l'élément trouvé  */

    assert(FLAT_ARRAY_IS_LOCKED(array));

    count = count_flat_array_items(array);

    switch (count)
    {
        case 0:
            result = NULL;
            break;

        case 1:

            assert(FLAT_ARRAY_HAS_NO_INDEX(array));

            item = GET_LONELY_ITEM(array);

            if (compar(key, item) == 0)
                result = item;
            else
                result = NULL;

            break;

        default:

            assert(!FLAT_ARRAY_HAS_NO_INDEX(array));

            extended = EXTENDED_ARRAY(array);

            if (bsearch_index(key, extended->items, extended->count, size, compar, &index))
                result = (void *)(((char *)extended->items) + index * size);
            else
                result = NULL;

            break;

    }

    return result;

}
