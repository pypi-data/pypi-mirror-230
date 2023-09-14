
/* Chrysalide - Outil d'analyse de fichiers binaires
 * meta.h - prototypes pour la description globale d'une définition Kaitai
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


#ifndef _PLUGINS_KAITAI_PARSERS_META_H
#define _PLUGINS_KAITAI_PARSERS_META_H


#include <glib-object.h>


#include <common/endianness.h>
#include <plugins/yaml/node.h>



#define G_TYPE_KAITAI_META            g_kaitai_meta_get_type()
#define G_KAITAI_META(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_META, GKaitaiMeta))
#define G_IS_KAITAI_META(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_META))
#define G_KAITAI_META_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_META, GKaitaiMetaClass))
#define G_IS_KAITAI_META_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_META))
#define G_KAITAI_META_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_META, GKaitaiMetaClass))


/* Description globale d'une définition Kaitai (instance) */
typedef struct _GKaitaiMeta GKaitaiMeta;

/* Description globale d'une définition Kaitai (classe) */
typedef struct _GKaitaiMetaClass GKaitaiMetaClass;


/* Indique le type défini pour une description globale Kaitai. */
GType g_kaitai_meta_get_type(void);

/* Construit une description globale Kaitai. */
GKaitaiMeta *g_kaitai_meta_new(GYamlNode *);

/* Fournit l'identifié associé à une définiton Kaitai. */
const char *g_kaitai_meta_get_id(const GKaitaiMeta *);

/* Fournit la désignation humaine d'une définiton Kaitai. */
const char *g_kaitai_meta_get_title(const GKaitaiMeta *);

/* Indique le boustime observé par défaut par une définiton. */
SourceEndian g_kaitai_meta_get_endian(const GKaitaiMeta *);



#endif  /* _PLUGINS_KAITAI_PARSERS_META_H */
