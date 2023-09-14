
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.h - prototypes pour l'encadrement des blocs de code
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


#ifndef _ANALYSIS_BLOCK_H
#define _ANALYSIS_BLOCK_H


#include <glib.h>
#include <glib-object.h>
#include <stdbool.h>


#include "../arch/instruction.h"
#include "../arch/vmpa.h"
#include "../common/bits.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../glibext/bufferview.h"
#endif
#include "../glibext/linesegment.h"



/* ----------------------------- BLOC DE CODE GENERIQUE ----------------------------- */


#define G_TYPE_CODE_BLOCK            g_code_block_get_type()
#define G_CODE_BLOCK(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CODE_BLOCK, GCodeBlock))
#define G_IS_CODE_BLOCK(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CODE_BLOCK))
#define G_CODE_BLOCK_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CODE_BLOCK, GCodeBlockClass))
#define G_IS_CODE_BLOCK_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CODE_BLOCK))
#define G_CODE_BLOCK_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CODE_BLOCK, GCodeBlockClass))


/* Description d'un bloc de code (instance) */
typedef struct _GCodeBlock GCodeBlock;

/* Description d'un bloc de code (classe) */
typedef struct _GCodeBlockClass GCodeBlockClass;


/* Indique le type défini pour un bloc de code. */
GType g_code_block_get_type(void);

/* Indique la liste des blocs de code dominés. */
const bitfield_t *g_code_block_get_domination(const GCodeBlock *);

/* Indique l'indice d'intégration du bloc dans une liste. */
size_t g_code_block_get_index(const GCodeBlock *);

/* Détermine si un bloc de code contient une adresse donnée. */
bool g_code_block_contains_addr(const GCodeBlock *, const vmpa2t *);

/* Fournit le rang du bloc de code dans le flot d'exécution. */
size_t g_code_block_get_rank(const GCodeBlock *);

/* Définit le rang du bloc de code dans le flot d'exécution. */
void g_code_block_set_rank(GCodeBlock *, size_t);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la représentation graphique d'un bloc de code. */
GBufferView *g_code_block_get_view(GCodeBlock *, segcnt_list *);

/* Construit un ensemble d'indications pour bloc. */
char *g_code_block_build_tooltip(const GCodeBlock *);

#endif



/* ------------------- DEFINITION DE LIAISONS ENTRE BLOCS DE CODE ------------------- */


/* Déscription d'une liaison entre deux blocs */
typedef struct _block_link_t
{
    GCodeBlock *linked;                     /* Autre bloc de code lié      */
    InstructionLinkType type;               /* Type de liaison             */

} block_link_t;


#define ref_block_link(l) g_object_ref(G_OBJECT((l)->linked));
#define unref_block_link(l) g_object_unref(G_OBJECT((l)->linked));


/* Compare deux liens entre blocs de code. */
int g_code_block_compare_links(const block_link_t *, const block_link_t *);

/* Compare deux liens entre blocs de code. */
int g_code_block_compare_links_reversed(const block_link_t *, const block_link_t *);

/* Fournit les détails des origines d'un bloc de code donné. */
block_link_t *g_code_block_get_sources(const GCodeBlock *, size_t *);

/* Fournit les détails des destinations de bloc de code. */
block_link_t *g_code_block_get_destinations(const GCodeBlock *, size_t *);



/* ------------------------- REGROUPEMENT EN LISTE DE BLOCS ------------------------- */


#define G_TYPE_BLOCK_LIST            g_block_list_get_type()
#define G_BLOCK_LIST(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BLOCK_LIST, GBlockList))
#define G_IS_BLOCK_LIST(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BLOCK_LIST))
#define G_BLOCK_LIST_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BLOCK_LIST, GBlockListClass))
#define G_IS_BLOCK_LIST_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BLOCK_LIST))
#define G_BLOCK_LIST_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BLOCK_LIST, GBlockListClass))


/* Description d'une liste de blocs de code (instance) */
typedef struct _GBlockList GBlockList;

/* Description d'une liste de blocs de code (classe) */
typedef struct _GBlockListClass GBlockListClass;


/* Indique le type défini pour une liste de blocs de code. */
GType g_block_list_get_type(void);

/* Crée une liste de blocs de code. */
GBlockList *g_block_list_new(size_t);

/* Compte le nombre de blocs de code représentés. */
size_t g_block_list_count_blocks(const GBlockList *);

/* Ajoute un bloc de code à une liste définie. */
void g_block_list_add_block(GBlockList *, GCodeBlock *, size_t);

/* Ajoute un bloc de code à une liste en construction. */
void g_block_list_append_block(GBlockList *, GCodeBlock *);

/* Fournit le bloc de code correspondant à un indice de liste. */
GCodeBlock *g_block_list_get_block(const GBlockList *, size_t);

/*  Recherche un bloc de code contenant une adresse donnée. */
GCodeBlock *g_block_list_find_by_addr(const GBlockList *, const vmpa2t *);



#endif  /* _ANALYSIS_BLOCK_H */
