
/* Chrysalide - Outil d'analyse de fichiers binaires
 * masked-int.h - prototypes internes pour la gestion d'une recherche de motif partielle
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_MASKED_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_MASKED_INT_H


#include "masked.h"


#include "../node-int.h"



/* Bribe de motif partielle pour recherches (instance) */
struct _GScanTokenNodeMasked
{
    GScanTokenNode parent;                  /* A laisser en premier        */

    masked_byte_t *bytes;                   /* Série d'octets masqués      */
    size_t len;                             /* Taille de cette série       */

    sized_binary_t *raw;                    /* Liste de motifs à couvrir   */
    tracked_scan_atom_t *atoms;             /* Atomes correspondants       */
    size_t count;                           /* Taille de cette liste       */
    size_t enrolled_count;                  /* Quantité avec identifiant   */

};

/* Bribe de motif partielle pour recherches (classe) */
struct _GScanTokenNodeMaskedClass
{
    GScanTokenNodeClass parent;             /* A laisser en premier        */

};


/* Met en place une bribe de motif partielle. */
bool g_scan_token_node_masked_create(GScanTokenNodeMasked *, const masked_byte_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_MASKED_INT_H */
