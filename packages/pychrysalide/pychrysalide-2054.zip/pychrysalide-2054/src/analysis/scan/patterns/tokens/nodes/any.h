
/* Chrysalide - Outil d'analyse de fichiers binaires
 * any.h - prototypes pour une suite d'octets quelconques
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_ANY_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_ANY_H


#include <glib-object.h>


#include "../node.h"



#define G_TYPE_SCAN_TOKEN_NODE_ANY            g_scan_token_node_any_get_type()
#define G_SCAN_TOKEN_NODE_ANY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE_ANY, GScanTokenNodeAny))
#define G_IS_SCAN_TOKEN_NODE_ANY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE_ANY))
#define G_SCAN_TOKEN_NODE_ANY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE_ANY, GScanTokenNodeAnyClass))
#define G_IS_SCAN_TOKEN_NODE_ANY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE_ANY))
#define G_SCAN_TOKEN_NODE_ANY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE_ANY, GScanTokenNodeAnyClass))


/* Espace constitué d'un ou plusieurs octets quelconques (instance) */
typedef struct _GScanTokenNodeAny GScanTokenNodeAny;

/* Espace constitué d'un ou plusieurs octets quelconques (classe) */
typedef struct _GScanTokenNodeAnyClass GScanTokenNodeAnyClass;


/* Indique le type défini pour une série d'octets quelconque, vide ou non. */
GType g_scan_token_node_any_get_type(void);

/* Construit un noeud pointant une série d'octets quelconques. */
GScanTokenNode *g_scan_token_node_any_new(const phys_t *, const phys_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_ANY_H */
