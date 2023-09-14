
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sequence.h - prototypes pour des décompositions séquentielles de motif de recherche
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_SEQUENCE_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_SEQUENCE_H


#include <glib-object.h>


#include "../node.h"



#define G_TYPE_SCAN_TOKEN_NODE_SEQUENCE            g_scan_token_node_sequence_get_type()
#define G_SCAN_TOKEN_NODE_SEQUENCE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE_SEQUENCE, GScanTokenNodeSequence))
#define G_IS_SCAN_TOKEN_NODE_SEQUENCE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE_SEQUENCE))
#define G_SCAN_TOKEN_NODE_SEQUENCE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE_SEQUENCE, GScanTokenNodeSequenceClass))
#define G_IS_SCAN_TOKEN_NODE_SEQUENCE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE_SEQUENCE))
#define G_SCAN_TOKEN_NODE_SEQUENCE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE_SEQUENCE, GScanTokenNodeSequenceClass))


/* Décompositions séquentielles de motif de recherche (instance) */
typedef struct _GScanTokenNodeSequence GScanTokenNodeSequence;

/* Décompositions séquentielles de motif de recherche (classe) */
typedef struct _GScanTokenNodeSequenceClass GScanTokenNodeSequenceClass;


/* Indique le type défini pour des décompositions séquentielles de motif de recherche. */
GType g_scan_token_node_sequence_get_type(void);

/* Construit une série de décompositions séquentielles de motif. */
GScanTokenNode *g_scan_token_node_sequence_new(GScanTokenNode *);

/* Ajoute un noeud à aux décompositions séquentielles de motif. */
void g_scan_token_node_sequence_add(GScanTokenNodeSequence *, GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_SEQUENCE_H */
