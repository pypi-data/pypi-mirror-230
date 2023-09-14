
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection.h - prototypes pour une collection de noeuds YAML de type "sequence" ou "mapping"
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


#ifndef PLUGINS_YAML_COLLECTION_H
#define PLUGINS_YAML_COLLECTION_H


#include <glib-object.h>
#include <stdbool.h>


#include "node.h"



#define G_TYPE_YAML_COLLEC            g_yaml_collection_get_type()
#define G_YAML_COLLEC(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_YAML_COLLEC, GYamlCollection))
#define G_IS_YAML_COLLEC(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_YAML_COLLEC))
#define G_YAML_COLLEC_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_YAML_COLLEC, GYamlCollectionClass))
#define G_IS_YAML_COLLEC_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_YAML_COLLEC))
#define G_YAML_COLLEC_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_YAML_COLLEC, GYamlCollectionClass))


/* Collection de noeuds au format YAML (instance) */
typedef struct _GYamlCollection GYamlCollection;

/* Collection de noeuds au format YAML (classe) */
typedef struct _GYamlCollectionClass GYamlCollectionClass;


/* Indique le type défini pour une collection de noeuds YAML. */
GType g_yaml_collection_get_type(void);

/* Construit une collection de noeuds YAML. */
GYamlCollection *g_yaml_collection_new(bool);

/* Indique la nature d'une collection YAML. */
bool g_yaml_collection_is_sequence(const GYamlCollection *);

/* Ajoute un noeud à une collection de noeuds YAML. */
void g_yaml_collection_add_node(GYamlCollection *, GYamlNode *);

/* Fournit la liste des noeuds intégrés dans une collection. */
GYamlNode **g_yaml_collection_get_nodes(const GYamlCollection *, size_t *);

/* Fournit le premier noeud intégré dans une collection. */
GYamlNode *g_yaml_collection_get_first_node(const GYamlCollection *);



#endif  /* PLUGINS_YAML_COLLECTION_H */
