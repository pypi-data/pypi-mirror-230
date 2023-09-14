
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection-int.h - prototypes internes pour la définition d'un noeud YAML
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


#ifndef PLUGINS_YAML_COLLECTION_INT_H
#define PLUGINS_YAML_COLLECTION_INT_H


#include "collection.h"


#include "node-int.h"



/* Collection de noeuds au format YAML (instance) */
struct _GYamlCollection
{
    GYamlNode parent;                       /* A laisser en premier        */

    bool is_seq;                            /* Nature de la collection     */

    GYamlNode **nodes;                      /* Sous-noeuds intégrés        */
    size_t count;                           /* Nombre de ces enfants       */

};

/* Collection de noeuds au format YAML (classe) */
struct _GYamlCollectionClass
{
    GYamlNodeClass parent;                  /* A laisser en premier        */

};


/* Met en place une collection de noeuds YAML. */
bool g_yaml_collection_create(GYamlCollection *, bool);



#endif  /* PLUGINS_YAML_COLLECTION_INT_H */
