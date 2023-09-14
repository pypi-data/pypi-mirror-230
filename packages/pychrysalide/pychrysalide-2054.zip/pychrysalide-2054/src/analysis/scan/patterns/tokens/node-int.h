
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node-int.h - prototypes internes pour la décomposition d'un motif de recherche en atomes assemblés
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODE_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODE_INT_H


#include "node.h"


#include "offset.h"



/* Prend acte d'une nouvelle propriété pour le noeud. */
typedef void (* apply_scan_token_node_flags_fc) (GScanTokenNode *, ScanTokenNodeFlags);

/* Noeuds clefs de l'arborescence mise en place */
typedef struct _scan_tree_points_t
{
    GScanTokenNode *first_node;             /* Premier noeud de traitement */
    GScanTokenNode *last_node;              /* Dernier noeud de traitement */

    GScanTokenNode *first_plain;            /* Premier noeud textuel       */
    GScanTokenNode *best_masked;            /* Noeud masqué le plus long   */

} scan_tree_points_t;


/* Parcourt une arborescence de noeuds et y relève des éléments. */
typedef void (* visit_scan_token_node_fc) (GScanTokenNode *, scan_tree_points_t *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
typedef bool (* enroll_scan_token_node_fc) (GScanTokenNode *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Transforme les correspondances locales en trouvailles. */
typedef void (* check_scan_token_node_fc) (const GScanTokenNode *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);


/* Décomposition d'un motif de recherche en atomes (instance) */
struct _GScanTokenNode
{
    GObject parent;                         /* A laisser en premier        */

    ScanTokenNodeFlags flags;               /* Propriétés particulières    */

};

/* Décomposition d'un motif de recherche en atomes (classe) */
struct _GScanTokenNodeClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    apply_scan_token_node_flags_fc apply;   /* Prise en compte de fanions  */

    visit_scan_token_node_fc visit;         /* Phase de répérage initial   */
    enroll_scan_token_node_fc enroll;       /* Inscription d'un motif      */

    check_scan_token_node_fc check_forward; /* Conversion en trouvailles   */
    check_scan_token_node_fc check_backward;/* Conversion en trouvailles   */

};


/* Parcourt une arborescence de noeuds et y relève des éléments. */
void g_scan_token_node_visit(GScanTokenNode *, scan_tree_points_t *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
bool _g_scan_token_node_enroll(GScanTokenNode *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Transforme les correspondances locales en trouvailles. */
void _g_scan_token_node_check_forward(const GScanTokenNode *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);

/* Transforme les correspondances locales en trouvailles. */
void _g_scan_token_node_check_backward(const GScanTokenNode *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODE_INT_H */
