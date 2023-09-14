
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node.h - prototypes pour une définition de noeud Yaml
 *
 * Copyright (C) 2019-2023 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef PLUGINS_YAML_NODE_H
#define PLUGINS_YAML_NODE_H


#include <glib-object.h>



#define G_TYPE_YAML_NODE            g_yaml_node_get_type()
#define G_YAML_NODE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_YAML_NODE, GYamlNode))
#define G_IS_YAML_NODE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_YAML_NODE))
#define G_YAML_NODE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_YAML_NODE, GYamlNodeClass))
#define G_IS_YAML_NODE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_YAML_NODE))
#define G_YAML_NODE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_YAML_NODE, GYamlNodeClass))


/* Noeud d'une arborescence au format YAML (instance) */
typedef struct _GYamlNode GYamlNode;

/* Noeud d'une arborescence au format YAML (classe) */
typedef struct _GYamlNodeClass GYamlNodeClass;


/* Indique le type défini pour un noeud d'arborescence Yaml. */
GType g_yaml_node_get_type(void);

/* Recherche le premier noeud correspondant à un chemin. */
GYamlNode *g_yaml_node_find_first_by_path(GYamlNode *, const char *);



#endif  /* PLUGINS_YAML_NODE_H */
