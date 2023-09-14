
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block-int.h - prototypes pour la définition interne des blocs de code
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_BLOCK_INT_H
#define _ANALYSIS_BLOCK_INT_H


#include "block.h"


#include "../common/array.h"



/* ----------------------------- BLOC DE CODE GENERIQUE ----------------------------- */


/* Détermine si un bloc de code contient une adresse donnée. */
typedef bool (* block_contains_fc) (const GCodeBlock *, const vmpa2t *);

/* Compare deux liens entre blocs de code. */
typedef int (* block_compare_links_fc) (const block_link_t *, const block_link_t *);

/* Fournit les détails des origines d'un bloc de code donné. */
typedef block_link_t * (* block_get_links_fc) (const GCodeBlock *, const GBlockList *, size_t *);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la représentation graphique d'un bloc de code. */
typedef GBufferView * (* block_build_view_fc) (const GCodeBlock *, segcnt_list *);

/* Construit un ensemble d'indications pour bloc. */
typedef char *(* block_build_tooltip_fc) (const GCodeBlock *);

#endif


/* Description d'un bloc de code (instance) */
struct _GCodeBlock
{
    GObject parent;                         /* A laisser en premier        */

    /* Référence circulaire */
    GBlockList *list;                       /* Lien vers l'ensemble        */

    bitfield_t *domination;                 /* Blocs dominés de l'ensemble */

    size_t index;                           /* Indice dans une liste       */
    size_t rank;                            /* Rang dans l'exécution       */

#ifdef INCLUDE_GTK_SUPPORT
    GBufferView *view;                      /* Représentation construite   */
#endif

};

/* Description d'un bloc de code (classe) */
struct _GCodeBlockClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    block_contains_fc contains;             /* Possession d'une adresse    */
    block_compare_links_fc cmp_links;       /* Comparaison de liens        */
    block_get_links_fc get_src;             /* Obtention des origines      */
    block_get_links_fc get_dest;            /* Obtention des destinations  */
#ifdef INCLUDE_GTK_SUPPORT
    block_build_view_fc build;              /* Construction d'une vue      */
    block_build_tooltip_fc build_tooltip;   /* Construction d'une bulle    */
#endif

};



#endif  /* _ANALYSIS_BLOCK_INT_H */
