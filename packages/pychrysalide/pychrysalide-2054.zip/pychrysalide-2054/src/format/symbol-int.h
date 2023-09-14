
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbol-int.h - prototypes pour la définition interne des symboles dans un binaire
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


#ifndef _FORMAT_SYMBOL_INT_H
#define _FORMAT_SYMBOL_INT_H


#include "symbol.h"
#include "../analysis/storage/serialize-int.h"
#include "../glibext/objhole.h"



/* Fournit une étiquette pour viser un symbole. */
typedef char * (* get_symbol_label_fc) (const GBinSymbol *);

/* Charge un contenu depuis une mémoire tampon. */
typedef bool (* load_symbol_fc) (GBinSymbol *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
typedef bool (* store_symbol_fc) (GBinSymbol *, GObjectStorage *, packed_buffer_t *);


/* Informations glissées dans la structure GObject de GBinSymbol */
typedef struct _sym_extra_data_t
{
    SymbolType stype;                       /* Type du symbole             */
    SymbolStatus status;                    /* Visibilité du symbole       */

    char nm_prefix;                         /* Eventuel préfixe "nm"       */

    SymbolFlag flags;                       /* Informations complémentaires*/

} sym_extra_data_t;

/* Encapsulation avec un verrou d'accès */
typedef union _symbol_obj_extra_t
{
    sym_extra_data_t data;                  /* Données embarquées          */
    lockable_obj_extra_t lockable;          /* Gestion d'accès aux fanions */

} symbol_obj_extra_t;


/* Symbole d'exécutable (instance) */
struct _GBinSymbol
{
    GObject parent;                         /* A laisser en premier        */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

    /**
     * L'inclusion des informations suivantes dépend de l'architecture.
     *
     * Si la structure GObject possède un trou, on remplit de préférence
     * ce dernier.
     */

    symbol_obj_extra_t extra;               /* Externalisation embarquée   */

#endif

    mrange_t range;                         /* Couverture mémoire          */

    char *alt;                              /* Nom alternatif              */

};

/* Symbole d'exécutable (classe) */
struct _GBinSymbolClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_symbol_label_fc get_label;          /* Obtention d'une étiquette   */

    load_symbol_fc load;                    /* Chargement depuis un tampon */
    store_symbol_fc store;                  /* Conservation dans un tampon */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_BIN_SYMBOL_EXTRA(sym) (sym_extra_data_t *)&sym->extra

#else

#   define GET_BIN_SYMBOL_EXTRA(sym) GET_GOBJECT_EXTRA(G_OBJECT(sym), sym_extra_data_t)

#endif



#endif  /* _FORMAT_SYMBOL_INT_H */
