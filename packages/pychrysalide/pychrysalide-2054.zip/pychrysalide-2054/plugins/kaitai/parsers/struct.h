
/* Chrysalide - Outil d'analyse de fichiers binaires
 * struct.h - prototypes pour la définition d'une structure Kaitai
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


#ifndef _PLUGINS_KAITAI_PARSERS_STRUCT_H
#define _PLUGINS_KAITAI_PARSERS_STRUCT_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>


#include "enum.h"
#include "meta.h"
#include "type.h"
#include "../record.h"



#define G_TYPE_KAITAI_STRUCT            g_kaitai_structure_get_type()
#define G_KAITAI_STRUCT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_STRUCT, GKaitaiStruct))
#define G_IS_KAITAI_STRUCT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_STRUCT))
#define G_KAITAI_STRUCT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_STRUCT, GKaitaiStructClass))
#define G_IS_KAITAI_STRUCT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_STRUCT))
#define G_KAITAI_STRUCT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_STRUCT, GKaitaiStructClass))


/* Spécification d'une structure Kaitai (instance) */
typedef struct _GKaitaiStruct GKaitaiStruct;

/* Spécification d'une structure Kaitai (classe) */
typedef struct _GKaitaiStructClass GKaitaiStructClass;


/* Indique le type défini pour une structure Kaitai. */
GType g_kaitai_structure_get_type(void);

/* Crée un nouvel interpréteur de structure Kaitai. */
GKaitaiStruct *g_kaitai_structure_new_from_text(const char *);

/* Crée un nouvel interpréteur de structure Kaitai. */
GKaitaiStruct *g_kaitai_structure_new_from_file(const char *);

/* Fournit la description globale d'une définition Kaitai. */
GKaitaiMeta *g_kaitai_structure_get_meta(const GKaitaiStruct *);

/* Recherche la définition d'un type nouveau pour Kaitai. */
GKaitaiType *g_kaitai_structure_find_sub_type(const GKaitaiStruct *, const char *);

/* Fournit un ensemble d'énumérations locales de la structure. */
GKaitaiEnum *g_kaitai_structure_get_enum(const GKaitaiStruct *, const sized_string_t *);

/* Parcourt un contenu binaire selon une description Kaitai. */
GMatchRecord *g_kaitai_structure_parse(GKaitaiStruct *, GBinContent *);



#endif  /* _PLUGINS_KAITAI_PARSERS_STRUCT_H */
