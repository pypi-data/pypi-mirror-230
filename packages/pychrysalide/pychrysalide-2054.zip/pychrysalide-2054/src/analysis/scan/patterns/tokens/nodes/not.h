
/* Chrysalide - Outil d'analyse de fichiers binaires
 * not.h - prototypes pour l'inversion de résultats de correspondances établis
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_NOT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_NOT_H


#include <glib-object.h>


#include "../node.h"
#include "../../../../../arch/archbase.h"



#define G_TYPE_SCAN_TOKEN_NODE_NOT            g_scan_token_node_not_get_type()
#define G_SCAN_TOKEN_NODE_NOT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_NODE_NOT, GScanTokenNodeNot))
#define G_IS_SCAN_TOKEN_NODE_NOT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_NODE_NOT))
#define G_SCAN_TOKEN_NODE_NOT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_NODE_NOT, GScanTokenNodeNotClass))
#define G_IS_SCAN_TOKEN_NODE_NOT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_NODE_NOT))
#define G_SCAN_TOKEN_NODE_NOT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_NODE_NOT, GScanTokenNodeNotClass))


/* Inversion de résultats de correspondances établis (instance) */
typedef struct _GScanTokenNodeNot GScanTokenNodeNot;

/* Inversion de résultats de correspondances établis (classe) */
typedef struct _GScanTokenNodeNotClass GScanTokenNodeNotClass;


/* Indique le type défini pour une inversion des résultats de correspondances. */
GType g_scan_token_node_not_get_type(void);

/* Construit une inversion de résultats de correspondances. */
GScanTokenNode *g_scan_token_node_not_new(GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_NOT_H */
