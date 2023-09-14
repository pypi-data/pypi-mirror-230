
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pair-int.h - prototypes internes pour la définition d'un noeud YAML
 *
 * Copyright (C) 2020-2023 Cyrille Bagard
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


#ifndef PLUGINS_YAML_PAIR_INT_H
#define PLUGINS_YAML_PAIR_INT_H


#include "pair.h"


#include <stdbool.h>


#include "node-int.h"



/* Noeud d'une arborescence au format YAML (instance) */
struct _GYamlPair
{
    GYamlNode parent;                       /* A laisser en premier        */

    char *key;                              /* Clef présente dans le noeud */
    YamlOriginalStyle key_style;            /* Forme d'origine associé     */

    char *value;                            /* Valeur associée             */
    YamlOriginalStyle value_style;          /* Forme d'origine associé     */

    GYamlCollection *children;              /* Collection de noeuds        */

};

/* Noeud d'une arborescence au format YAML (classe) */
struct _GYamlPairClass
{
    GYamlNodeClass parent;                  /* A laisser en premier        */

};


/* Met en place une pair clef/valeur YAML. */
bool g_yaml_pair_create(GYamlPair *, const char *, YamlOriginalStyle, const char *, YamlOriginalStyle);



#endif  /* PLUGINS_YAML_PAIR_INT_H */
