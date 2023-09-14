
/* Chrysalide - Outil d'analyse de fichiers binaires
 * enum.h - prototypes pour la gestion des énumérations Kaitai
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _PLUGINS_KAITAI_PARSERS_ENUM_H
#define _PLUGINS_KAITAI_PARSERS_ENUM_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>


#include <common/szstr.h>
#include <plugins/yaml/node.h>


#include "../expression.h"



#define G_TYPE_KAITAI_ENUM            g_kaitai_enum_get_type()
#define G_KAITAI_ENUM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_ENUM, GKaitaiEnum))
#define G_IS_KAITAI_ENUM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_ENUM))
#define G_KAITAI_ENUM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_ENUM, GKaitaiEnumClass))
#define G_IS_KAITAI_ENUM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_ENUM))
#define G_KAITAI_ENUM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_ENUM, GKaitaiEnumClass))


/* Définition d'un ensemble d'énumérations Kaitai (instance) */
typedef struct _GKaitaiEnum GKaitaiEnum;

/* Définition d'un ensemble d'énumérations Kaitai (classe) */
typedef struct _GKaitaiEnumClass GKaitaiEnumClass;


/* Indique le type défini pour un ensemble d'énumérations Kaitai. */
GType g_kaitai_enum_get_type(void);

/* Construit un groupe d'énumérations Kaitai. */
GKaitaiEnum *g_kaitai_enum_new(GYamlNode *);

/* Fournit le nom principal d'une énumération. */
const char *g_kaitai_enum_get_name(const GKaitaiEnum *);

/* Traduit une étiquette brute en constante d'énumération. */
bool g_kaitai_enum_find_value(const GKaitaiEnum *, const sized_string_t *, resolved_value_t *);

/* Traduit une constante d'énumération en étiquette brute. */
char *g_kaitai_enum_find_label(const GKaitaiEnum *, const resolved_value_t *, bool);

/* Traduit une constante d'énumération en documentation. */
char *g_kaitai_enum_find_documentation(const GKaitaiEnum *, const resolved_value_t *);



#endif  /* _PLUGINS_KAITAI_PARSERS_ENUM_H */
