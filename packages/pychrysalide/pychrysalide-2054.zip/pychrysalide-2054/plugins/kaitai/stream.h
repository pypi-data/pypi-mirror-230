
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.h - prototypes pour les données associées à un flux de données Kaitai
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


#ifndef PLUGINS_KAITAI_STREAM_H
#define PLUGINS_KAITAI_STREAM_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>



#define G_TYPE_KAITAI_STREAM            g_kaitai_stream_get_type()
#define G_KAITAI_STREAM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_STREAM, GKaitaiStream))
#define G_IS_KAITAI_STREAM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_STREAM))
#define G_KAITAI_STREAM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_STREAM, GKaitaiStreamClass))
#define G_IS_KAITAI_STREAM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_STREAM))
#define G_KAITAI_STREAM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_STREAM, GKaitaiStreamClass))


/* Flux de données à disposition d'une analyse Kaitai (instance) */
typedef struct _GKaitaiStream GKaitaiStream;

/* Flux de données à disposition d'une analyse Kaitai (classe) */
typedef struct _GKaitaiStreamClass GKaitaiStreamClass;


/* Indique le type défini pour un flux de données manipulé par une lecture Kaitai. */
GType g_kaitai_stream_get_type(void);

/* Rassemble les éléments constituant un flux de données Kaitai. */
GKaitaiStream *g_kaitai_stream_new(GBinContent *, const vmpa2t *);

/* Indique le contenu de données binaires lié au flux Kaitai. */
GBinContent *g_kaitai_stream_get_content(const GKaitaiStream *);

/* Détermine si la fin des données a été atteinte. */
bool g_kaitai_stream_has_reached_eof(const GKaitaiStream *);



#endif  /* PLUGINS_KAITAI_STREAM_H */
