
/* Chrysalide - Outil d'analyse de fichiers binaires
 * meta-int.h - prototypes internes pour la description globale d'une définition Kaitai
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


#ifndef PLUGINS_KAITAI_PARSERS_META_INT_H
#define PLUGINS_KAITAI_PARSERS_META_INT_H


#include "meta.h"



/* Description globale d'une définition Kaitai (instance) */
struct _GKaitaiMeta
{
    GObject parent;                         /* A laisser en premier        */

    char *id;                               /* Identifiant attribué        */
    char *title;                            /* Désignation de la définition*/

    SourceEndian endian;                    /* Boutisme par défaut         */

};

/* Description globale d'une définition Kaitai (classe) */
struct _GKaitaiMetaClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Met en place une description globale Kaitai. */
bool g_kaitai_meta_create(GKaitaiMeta *, GYamlNode *);



#endif  /* PLUGINS_KAITAI_PARSERS_META_INT_H */
