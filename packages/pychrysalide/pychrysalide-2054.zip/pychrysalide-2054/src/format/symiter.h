
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symiter.h - prototypes pour le parcours simplifié d'un ensemble de symboles
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


#ifndef _FORMAT_SYMITER_H
#define _FORMAT_SYMITER_H


#include "format.h"



/* Suivi d'un parcours de symboles */
typedef struct _sym_iter_t sym_iter_t;


/* Construit un itérateur pour parcourir des symboles. */
sym_iter_t *create_symbol_iterator(GBinFormat *, size_t);

/* Détruit un itérateur mis en place. */
void delete_symbol_iterator(sym_iter_t *);

/* Limite le parcours des symboles à une zone donnée. */
void restrict_symbol_iterator(sym_iter_t *, const mrange_t *);

/* Fournit le symbole courant de l'itérateur. */
GBinSymbol *get_symbol_iterator_current(sym_iter_t *);

/* Fournit le symbole qui en précède un autre. */
GBinSymbol *get_symbol_iterator_prev(sym_iter_t *);

/* Fournit le symbole qui en suit un autre. */
GBinSymbol *get_symbol_iterator_next(sym_iter_t *);



#endif  /* _FORMAT_SYMITER_H */
