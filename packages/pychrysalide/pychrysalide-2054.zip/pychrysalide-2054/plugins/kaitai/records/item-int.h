
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item-int.h - prototypes internes pour la conservation d'une correspondance entre attribut et binaire
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


#ifndef _PLUGINS_KAITAI_RECORDS_ITEM_INT_H
#define _PLUGINS_KAITAI_RECORDS_ITEM_INT_H


#include "item.h"


#include "../record-int.h"



/* Correspondance établie entre un attribut et du binaire (instance) */
struct _GRecordItem
{
    GMatchRecord parent;                    /* A laisser en premier        */

    mrange_t range;                         /* Zone de binaire couverte    */
    SourceEndian endian;                    /* Boutisme des données imposé */

};

/* Correspondance établie entre un attribut et du binaire (classe) */
struct _GRecordItemClass
{
    GMatchRecordClass parent;               /* A laisser en premier        */

};


/* Met en place une correspondance entre attribut et binaire. */
bool g_record_item_create(GRecordItem *, GKaitaiAttribute *, GBinContent *, const mrange_t *, SourceEndian);



#endif  /* _PLUGINS_KAITAI_RECORDS_ITEM_INT_H */
