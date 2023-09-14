
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.h - prototypes pour la manipulation optimisée de tableaux au niveau de l'empreinte mémoire
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _COMMON_ARRAY_H
#define _COMMON_ARRAY_H


#include <stdlib.h>
#include <sys/types.h>



/* Type déclaratif de tableau compressé, à 0 ou 1 élément */
typedef void *flat_array_t;

/* Parcours d'éléments */
typedef void (* item_notify_cb) (void *);


/* Verrouille l'accès à un tableau compressé. */
void lock_flat_array(flat_array_t **);

/* Déverrouille l'accès à un tableau compressé. */
void unlock_flat_array(flat_array_t **);

/* Réinitialise un tableau sans traitement excessif. */
void reset_flat_array(flat_array_t **);

/* Copie le contenu d'un tableau d'éléments dans un autre. */
void copy_flat_array_items(flat_array_t **, flat_array_t **, size_t, item_notify_cb);

/* Indique la quantité d'éléments présents dans le tableau. */
size_t count_flat_array_items(const flat_array_t *);

/* Ajoute un élément supplémentaire à un tableau. */
void add_item_to_flat_array(flat_array_t **, const void *, size_t);

/* Ajoute un élément supplémentaire à un tableau trié. */
void insert_item_into_flat_array(flat_array_t **, void *, size_t, __compar_fn_t);

/* Remplace un élément d'un tableau compressé par un autre. */
void rpl_item_in_flat_array(flat_array_t *, size_t, void *, size_t);

/* Retire un élément existant d'un tableau. */
void rem_item_from_flat_array(flat_array_t **, size_t, size_t);

/* Fournit un élément présent dans un tableau compressé. */
void *get_flat_array_item(flat_array_t *, size_t, size_t);

/* Recherche un élément dans un tableau trié. */
void *find_item_in_flat_array(flat_array_t *, size_t, __compar_fn_t, const void *);



#endif  /* _COMMON_ARRAY_H */
