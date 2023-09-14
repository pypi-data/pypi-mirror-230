
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sequence-int.h - prototypes internes pour des décompositions séquentielles de motif de recherche
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_SEQUENCE_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_SEQUENCE_INT_H


#include "sequence.h"


#include "../node-int.h"



/* Décompositions séquentielles de motif de recherche (instance) */
struct _GScanTokenNodeSequence
{
    GScanTokenNode parent;                  /* A laisser en premier        */

    GScanTokenNode **children;              /* Sous-noeuds à représenter   */
    size_t count;                           /* Taille de cette liste       */

};

/* Décompositions séquentielles de motif de recherche (classe) */
struct _GScanTokenNodeSequenceClass
{
    GScanTokenNodeClass parent;             /* A laisser en premier        */

};


/* Met en place une série de décompositions séquentielles. */
bool g_scan_token_node_sequence_create(GScanTokenNodeSequence *, GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_SEQUENCE_INT_H */
