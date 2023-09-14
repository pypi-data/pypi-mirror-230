
/* Chrysalide - Outil d'analyse de fichiers binaires
 * struct-int.h - prototypes internes pour la définition d'une structure Kaitai
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


#ifndef PLUGINS_KAITAI_PARSERS_STRUCT_INT_H
#define PLUGINS_KAITAI_PARSERS_STRUCT_INT_H


#include "attribute.h"
#include "instance.h"
#include "struct.h"
#include "../parser-int.h"



/* Spécification d'une structure Kaitai (instance) */
struct _GKaitaiStruct
{
    GKaitaiParser parent;                   /* A laisser en premier        */

    GKaitaiMeta *meta;                      /* Description globale         */

    GKaitaiAttribute **seq_items;           /* Sous-attributs présents     */
    size_t seq_items_count;                 /* Quantité de ces attributs   */

    GKaitaiType **types;                    /* Types particuliers définis  */
    size_t types_count;                     /* Quantité de ces types       */

    GKaitaiInstance **instances;            /* Instances prises en charge  */
    size_t instances_count;                 /* Quantité de ces instances   */

    GKaitaiEnum **enums;                    /* Enumérations locales        */
    size_t enums_count;                     /* Quantité de ces énumérations*/

};

/* Spécification d'une structure Kaitai (classe) */
struct _GKaitaiStructClass
{
    GKaitaiParserClass parent;              /* A laisser en premier        */

};


/* Met en place un interpréteur de définitions Kaitai. */
bool g_kaitai_structure_create_from_text(GKaitaiStruct *, const char *);

/* Met en place un interpréteur de définitions Kaitai. */
bool g_kaitai_structure_create_from_file(GKaitaiStruct *, const char *);

/* Met en place un lecteur de définitions Kaitai. */
bool g_kaitai_structure_create(GKaitaiStruct *, GYamlNode *);



#endif  /* PLUGINS_KAITAI_PARSERS_STRUCT_INT_H */
