
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plain.h - prototypes pour la gestion d'une recherche de motif textuel
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_PLAIN_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_PLAIN_H


#include <glib-object.h>


#include "../node.h"
#include "../../modifier.h"
#include "../../../../../common/szstr.h"



#define G_TYPE_SCAN_TOKEN_NODE_PLAIN            g_scan_token_node_plain_get_type()
#define G_SCAN_TOKEN_NODE_PLAIN(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE_PLAIN, GScanTokenNodePlain))
#define G_IS_SCAN_TOKEN_NODE_PLAIN(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE_PLAIN))
#define G_SCAN_TOKEN_NODE_PLAIN_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE_PLAIN, GScanTokenNodePlainClass))
#define G_IS_SCAN_TOKEN_NODE_PLAIN_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE_PLAIN))
#define G_SCAN_TOKEN_NODE_PLAIN_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE_PLAIN, GScanTokenNodePlainClass))


/* Bribe de motif textuelle pour recherches (instance) */
typedef struct _GScanTokenNodePlain GScanTokenNodePlain;

/* Bribe de motif textuelle pour recherches (classe) */
typedef struct _GScanTokenNodePlainClass GScanTokenNodePlainClass;


/* Propriétés d'un élément textuel à rechercher */
typedef enum _ScanPlainNodeFlags
{
    SPNF_NONE             = (0 << 0),       /* Aucune particularité        */
    SPNF_CASE_INSENSITIVE = (1 << 0),       /* Ignorance de la casse       */

    /**
     * Les deux propriétés suivantes sont récupérées et traitées
     * au niveau du Token propriétaire.
     */

    SPNF_FULLWORD         = (1 << 1),       /* Recherche de mot entier     */
    SPNF_PRIVATE          = (1 << 2),       /* Marque privative            */

} ScanPlainNodeFlags;


/* Indique le type défini pour un noeud représentant une bribe de texte à retrouver. */
GType g_scan_token_node_plain_get_type(void);

/* Construit un noeud représentant un motif textuel. */
GScanTokenNode *g_scan_token_node_plain_new(const sized_binary_t *, GScanTokenModifier *, ScanPlainNodeFlags);

/* Indique les propriétés particulières d'un noeud de texte. */
ScanPlainNodeFlags g_scan_token_node_plain_get_flags(const GScanTokenNodePlain *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_PLAIN_H */
