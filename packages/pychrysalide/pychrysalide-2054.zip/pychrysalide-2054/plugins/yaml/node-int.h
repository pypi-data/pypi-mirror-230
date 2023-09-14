
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node-int.h - prototypes internes pour la définition d'un noeud YAML
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


#ifndef PLUGINS_YAML_NODE_INT_H
#define PLUGINS_YAML_NODE_INT_H


#include "node.h"



/* Recherche le premier noeud correspondant à un chemin. */
typedef GYamlNode * (* find_first_yaml_node_fc) (GYamlNode *, const char *);


/* Noeud d'une arborescence au format YAML (instance) */
struct _GYamlNode
{
    GObject parent;                         /* A laisser en premier        */

};

/* Noeud d'une arborescence au format YAML (classe) */
struct _GYamlNodeClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    find_first_yaml_node_fc find;           /* Recherche par chemin        */

};



#endif  /* PLUGINS_YAML_NODE_INT_H */
