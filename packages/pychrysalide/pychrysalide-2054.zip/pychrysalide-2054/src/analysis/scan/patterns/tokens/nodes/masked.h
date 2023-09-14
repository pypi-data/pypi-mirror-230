
/* Chrysalide - Outil d'analyse de fichiers binaires
 * masked.h - prototypes pour la gestion d'une recherche de motif partielle
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_MASKED_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_MASKED_H


#include <glib-object.h>


#include "../atom.h"
#include "../node.h"
#include "../../../../../arch/archbase.h"



#define G_TYPE_SCAN_TOKEN_NODE_MASKED            g_scan_token_node_masked_get_type()
#define G_SCAN_TOKEN_NODE_MASKED(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE_MASKED, GScanTokenNodeMasked))
#define G_IS_SCAN_TOKEN_NODE_MASKED(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE_MASKED))
#define G_SCAN_TOKEN_NODE_MASKED_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE_MASKED, GScanTokenNodeMaskedClass))
#define G_IS_SCAN_TOKEN_NODE_MASKED_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE_MASKED))
#define G_SCAN_TOKEN_NODE_MASKED_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE_MASKED, GScanTokenNodeMaskedClass))


/* Bribe de motif partielle pour recherches (instance) */
typedef struct _GScanTokenNodeMasked GScanTokenNodeMasked;

/* Bribe de motif partielle pour recherches (classe) */
typedef struct _GScanTokenNodeMaskedClass GScanTokenNodeMaskedClass;


/* Mémorisation d'un octet visé avec son masque */
typedef struct _masked_byte_t
{
    bin_t value;                            /* Valeur de l'octet visé      */
    bin_t mask;                             /* Masque à appliquer          */

} masked_byte_t;


/* Indique le type défini pour un noeud représentant une bribe partielle à retrouver. */
GType g_scan_token_node_masked_get_type(void);

/* Construit une bribe de motif partielle. */
GScanTokenNode *g_scan_token_node_masked_new(const masked_byte_t *);

/* Enregistre la valeur d'octet à rechercher avec son masque. */
void g_scan_token_node_masked_add(GScanTokenNodeMasked *, const masked_byte_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_MASKED_H */
