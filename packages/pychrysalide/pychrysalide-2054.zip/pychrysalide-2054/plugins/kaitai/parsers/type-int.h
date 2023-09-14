
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type-int.h - prototypes internes pour la définition d'un type particulier pour Kaitai
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


#ifndef PLUGINS_KAITAI_PARSERS_TYPE_INT_H
#define PLUGINS_KAITAI_PARSERS_TYPE_INT_H


#include "struct-int.h"
#include "type.h"



/* Définition d'un type particulier nouveau pour Kaitai (instance) */
struct _GKaitaiType
{
    GKaitaiStruct parent;                   /* A laisser en premier        */

    char *name;                             /* Nom du type particulier     */

};

/* Définition d'un type particulier nouveau pour Kaitai (classe) */
struct _GKaitaiTypeClass
{
    GKaitaiStructClass parent;              /* A laisser en premier        */

};


/* Met en place un lecteur de type pour Kaitai. */
bool g_kaitai_type_create(GKaitaiType *, GYamlNode *);



#endif  /* PLUGINS_KAITAI_PARSERS_TYPE_INT_H */
