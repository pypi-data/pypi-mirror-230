
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.h - prototypes pour la définition d'un type particulier pour Kaitai
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


#ifndef _PLUGINS_KAITAI_PARSERS_TYPE_H
#define _PLUGINS_KAITAI_PARSERS_TYPE_H


#include <glib-object.h>
#include <stdbool.h>


#include <plugins/yaml/node.h>



#define G_TYPE_KAITAI_TYPE            g_kaitai_type_get_type()
#define G_KAITAI_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_TYPE, GKaitaiType))
#define G_IS_KAITAI_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_TYPE))
#define G_KAITAI_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_TYPE, GKaitaiTypeClass))
#define G_IS_KAITAI_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_TYPE))
#define G_KAITAI_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_TYPE, GKaitaiTypeClass))


/* Définition d'un type particulier nouveau pour Kaitai (instance) */
typedef struct _GKaitaiType GKaitaiType;

/* Définition d'un type particulier nouveau pour Kaitai (classe) */
typedef struct _GKaitaiTypeClass GKaitaiTypeClass;


/* Indique le type défini pour un type particulier pour Kaitai. */
GType g_kaitai_type_get_type(void);

/* Construit un lecteur de type pour Kaitai. */
GKaitaiType *g_kaitai_type_new(GYamlNode *);

/* Indique le nom de scène du type représenté. */
const char *g_kaitai_type_get_name(const GKaitaiType *);



#endif  /* _PLUGINS_KAITAI_PARSERS_TYPE_H */
