
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pair.h - prototypes pour un noeud Yaml de paire clef/valeur
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


#ifndef PLUGINS_YAML_PAIR_H
#define PLUGINS_YAML_PAIR_H


#include <glib-object.h>
#include <stdbool.h>


#include "collection.h"
#include "node.h"


#define G_TYPE_YAML_PAIR            g_yaml_pair_get_type()
#define G_YAML_PAIR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_YAML_PAIR, GYamlPair))
#define G_IS_YAML_PAIR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_YAML_PAIR))
#define G_YAML_PAIR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_YAML_PAIR, GYamlPairClass))
#define G_IS_YAML_PAIR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_YAML_PAIR))
#define G_YAML_PAIR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_YAML_PAIR, GYamlPairClass))


/* Noeud d'une arborescence au format Yaml (instance) */
typedef struct _GYamlPair GYamlPair;

/* Noeud d'une arborescence au format Yaml (classe) */
typedef struct _GYamlPairClass GYamlPairClass;


/* Format d'origine des éléments du couple clef/valeur */
typedef enum _YamlOriginalStyle
{
    YOS_PLAIN,                              /* Mode brut, par défaut       */
    YOS_SINGLE_QUOTED,                      /* Encadré simplement          */
    YOS_DOUBLE_QUOTED,                      /* ENcadré avec des guillemets */

} YamlOriginalStyle;


/* Indique le type défini pour un noeud d'arborescence Yaml. */
GType g_yaml_pair_get_type(void);

/* Construit un noeud d'arborescence Yaml. */
GYamlPair *g_yaml_pair_new(const char *, YamlOriginalStyle, const char *, YamlOriginalStyle);

/* Fournit la clef représentée dans une paire en Yaml. */
const char *g_yaml_pair_get_key(const GYamlPair *);

/* Indique le format d'origine YAML associé à la clef. */
YamlOriginalStyle g_yaml_pair_get_key_style(const GYamlPair *);

/* Fournit l'éventuelle valeur d'une paire en Yaml. */
const char *g_yaml_pair_get_value(const GYamlPair *);

/* Indique le format d'origine YAML associé à la valeur. */
YamlOriginalStyle g_yaml_pair_get_value_style(const GYamlPair *);

/* Rassemble une éventuelle séquence de valeurs attachées. */
char *g_yaml_pair_aggregate_value(const GYamlPair *);

/* Attache une collection de noeuds Yaml à un noeud. */
void g_yaml_pair_set_children(GYamlPair *, GYamlCollection *);

/* Fournit une éventuelle collection rattachée à un noeud. */
GYamlCollection *g_yaml_pair_get_children(const GYamlPair *);



#endif  /* PLUGINS_YAML_PAIR_H */
