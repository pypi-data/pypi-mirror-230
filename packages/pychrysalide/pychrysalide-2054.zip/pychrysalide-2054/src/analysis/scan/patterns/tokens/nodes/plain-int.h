
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plain-int.h - prototypes internes pour la gestion d'une recherche de motif textuel
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_PLAIN_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_PLAIN_INT_H


#include "plain.h"


#include "../atom.h"
#include "../node-int.h"



/* Bribe de motif textuelle pour recherches (instance) */
struct _GScanTokenNodePlain
{
    GScanTokenNode parent;                  /* A laisser en premier        */

    sized_binary_t orig;                    /* Motif d'origine avant modifs*/
    GScanTokenModifier *modifier;           /* Transformateur pour le motif*/
    ScanPlainNodeFlags flags;               /* Fanions associés au motif   */

    sized_binary_t *raw;                    /* Liste de motifs à couvrir   */
    tracked_scan_atom_t *atoms;             /* Atomes correspondants       */
    size_t count;                           /* Taille de cette liste       */

};

/* Bribe de motif textuelle pour recherches (instance) */
struct _GScanTokenNodePlainClass
{
    GScanTokenNodeClass parent;             /* A laisser en premier        */

};


/* Met en place un noeud représentant un motif textuel. */
bool g_scan_token_node_plain_create(GScanTokenNodePlain *, const sized_binary_t *, GScanTokenModifier *, ScanPlainNodeFlags);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_PLAIN_INT_H */
