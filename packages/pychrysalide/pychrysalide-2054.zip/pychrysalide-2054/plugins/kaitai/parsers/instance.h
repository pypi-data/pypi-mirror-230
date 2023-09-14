
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instance.h - prototypes pour la spécification d'une instance Kaitai
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _PLUGINS_KAITAI_PARSERS_INSTANCE_H
#define _PLUGINS_KAITAI_PARSERS_INSTANCE_H


#include <glib-object.h>


#include <plugins/yaml/node.h>


#include "../expression.h"
#include "../scope.h"



#define G_TYPE_KAITAI_INSTANCE            g_kaitai_instance_get_type()
#define G_KAITAI_INSTANCE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_INSTANCE, GKaitaiInstance))
#define G_IS_KAITAI_INSTANCE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_INSTANCE))
#define G_KAITAI_INSTANCE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_INSTANCE, GKaitaiInstanceClass))
#define G_IS_KAITAI_INSTANCE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_INSTANCE))
#define G_KAITAI_INSTANCE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_INSTANCE, GKaitaiInstanceClass))


/* Spécification d'une instance Kaitai (instance) */
typedef struct _GKaitaiInstance GKaitaiInstance;

/* Spécification d'une instance Kaitai (classe) */
typedef struct _GKaitaiInstanceClass GKaitaiInstanceClass;


/* Indique le type défini pour une instance de la spécification Kaitai. */
GType g_kaitai_instance_get_type(void);

/* Construit un lecteur d'instance Kaitai. */
GKaitaiInstance *g_kaitai_instance_new(GYamlNode *);

/* Indique le nom attribué à une instance Kaitai. */
const char *g_kaitai_instance_get_name(const GKaitaiInstance *);

/* Détermine la valeur d'un élément Kaitai entier calculé. */
bool g_kaitai_instance_compute_value(const GKaitaiInstance *, const kaitai_scope_t *, resolved_value_t *);



#endif  /* _PLUGINS_KAITAI_PARSERS_INSTANCE_H */
