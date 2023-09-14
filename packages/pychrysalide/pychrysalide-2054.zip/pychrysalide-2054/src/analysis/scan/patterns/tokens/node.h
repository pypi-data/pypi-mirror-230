
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node.h - prototypes pour la décomposition d'un motif de recherche en atomes assemblés
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODE_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODE_H


#include <glib-object.h>
#include <stdbool.h>


#include "../backend.h"
#include "../../context.h"
#include "../../matches/pending.h"


#define G_TYPE_SCAN_TOKEN_NODE            g_scan_token_node_get_type()
#define G_SCAN_TOKEN_NODE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE, GScanTokenNode))
#define G_IS_SCAN_TOKEN_NODE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE))
#define G_SCAN_TOKEN_NODE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE, GScanTokenNodeClass))
#define G_IS_SCAN_TOKEN_NODE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE))
#define G_SCAN_TOKEN_NODE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE, GScanTokenNodeClass))


/* Décomposition d'un motif de recherche en atomes (instance) */
typedef struct _GScanTokenNode GScanTokenNode;

/* Décomposition d'un motif de recherche en atomes (classe) */
typedef struct _GScanTokenNodeClass GScanTokenNodeClass;


/* Propriétés particulières pour noeud d'analyse */
typedef enum _ScanTokenNodeFlags
{
    STNF_NONE  = (0 << 0),                  /* Absence de singularité      */
    STNF_PROD  = (1 << 0),                  /* Absence de singularité      */
    STNF_FIRST = (1 << 1),                  /* Premier noeud de traitement */   /* REMME ? */
    STNF_LAST  = (1 << 2),                  /* Dernier noeud de traitement */   /* REMME ? */
    STNF_MAIN  = (1 << 3),                  /* Point de départ d'analyse   */

} ScanTokenNodeFlags;


/* Indique le type défini pour un élément décomposant un motif d'octets à rechercher. */
GType g_scan_token_node_get_type(void);

/* Indique les propriétés particulières d'un noeud d'analyse. */
ScanTokenNodeFlags g_scan_token_node_get_flags(const GScanTokenNode *);

/* Marque le noeud avec des propriétés particulières. */
void g_scan_token_node_set_flags(GScanTokenNode *, ScanTokenNodeFlags);

/* Détermine et prépare les éléments clefs d'une arborescence. */
bool g_scan_token_node_setup_tree(GScanTokenNode *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
bool g_scan_token_node_enroll(GScanTokenNode *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Transforme les correspondances locales en trouvailles. */
void g_scan_token_node_check_forward(const GScanTokenNode *, GScanContext *, GBinContent *, pending_matches_t *);

/* Transforme les correspondances locales en trouvailles. */
void g_scan_token_node_check_backward(const GScanTokenNode *, GScanContext *, GBinContent *, pending_matches_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODE_H */
