
/* Chrysalide - Outil d'analyse de fichiers binaires
 * choice.h - prototypes pour des décompositions alternatives de motif de recherche
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_CHOICE_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_CHOICE_H


#include <glib-object.h>


#include "../node.h"



#define G_TYPE_SCAN_TOKEN_NODE_CHOICE            g_scan_token_node_choice_get_type()
#define G_SCAN_TOKEN_NODE_CHOICE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE_CHOICE, GScanTokenNodeChoice))
#define G_IS_SCAN_TOKEN_NODE_CHOICE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE_CHOICE))
#define G_SCAN_TOKEN_NODE_CHOICE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE_CHOICE, GScanTokenNodeChoiceClass))
#define G_IS_SCAN_TOKEN_NODE_CHOICE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE_CHOICE))
#define G_SCAN_TOKEN_NODE_CHOICE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE_CHOICE, GScanTokenNodeChoiceClass))


/* Décompositions alternatives de motif de recherche (instance) */
typedef struct _GScanTokenNodeChoice GScanTokenNodeChoice;

/* Décompositions alternatives de motif de recherche (classe) */
typedef struct _GScanTokenNodeChoiceClass GScanTokenNodeChoiceClass;


/* Indique le type défini pour des décompositions alternatives de motif de recherche. */
GType g_scan_token_node_choice_get_type(void);

/* Construit une série de décompositions alternatives de motif. */
GScanTokenNode *g_scan_token_node_choice_new(void);

/* Ajoute un noeud à aux décompositions alternatives de motif. */
void g_scan_token_node_choice_add(GScanTokenNodeChoice *, GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_CHOICE_H */
