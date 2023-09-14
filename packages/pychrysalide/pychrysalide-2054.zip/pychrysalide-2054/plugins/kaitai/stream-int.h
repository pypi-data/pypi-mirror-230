
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream-int.h - prototypes pour les données associées à un flux de données Kaitai
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


#ifndef PLUGINS_KAITAI_STREAM_INT_H
#define PLUGINS_KAITAI_STREAM_INT_H


#include "stream.h"



/* Flux de données à disposition d'une analyse Kaitai (instance) */
struct _GKaitaiStream
{
    GObject parent;                         /* A laisser en premier        */

    GBinContent *content;                   /* Contenu brut manipulé       */
    vmpa2t pos;                             /* Tête de lecture dans le flux*/

};

/* Flux de données à disposition d'une analyse Kaitai (classe) */
struct _GKaitaiStreamClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Met en place un flux de données pour Kaitai. */
bool g_kaitai_stream_create(GKaitaiStream *, GBinContent *, const vmpa2t *);



#endif  /* PLUGINS_KAITAI_STREAM_INT_H */
