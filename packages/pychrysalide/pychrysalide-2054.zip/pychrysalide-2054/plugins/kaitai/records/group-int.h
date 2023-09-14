
/* Chrysalide - Outil d'analyse de fichiers binaires
 * group-int.h - prototypes internes pour la conservation d'un groupe de correspondance avec du binaire
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


#ifndef _PLUGINS_KAITAI_RECORDS_GROUP_INT_H
#define _PLUGINS_KAITAI_RECORDS_GROUP_INT_H


#include "group.h"


#include "../record-int.h"



/* Groupe de correspondances établies entre attributs et binaire (instance) */
struct _GRecordGroup
{
    GMatchRecord parent;                    /* A laisser en premier        */

    GMatchRecord **children;                /* Sous-correspondances        */
    size_t count;                           /* Taille de cette série       */

};

/* Groupe de correspondances établies entre attributs et binaire (classe) */
struct _GRecordGroupClass
{
    GMatchRecordClass parent;               /* A laisser en premier        */

};


/* Met en place une série de correspondances attribut/binaire. */
bool g_record_group_create(GRecordGroup *, GKaitaiStruct *, GBinContent *);



#endif  /* _PLUGINS_KAITAI_RECORDS_GROUP_INT_H */
