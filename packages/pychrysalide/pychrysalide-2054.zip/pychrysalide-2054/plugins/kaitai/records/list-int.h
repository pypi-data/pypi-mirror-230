
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list-int.h - prototypes internes pour la conservation d'une liste de correspondance avec du binaire
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


#ifndef _PLUGINS_KAITAI_RECORDS_LIST_INT_H
#define _PLUGINS_KAITAI_RECORDS_LIST_INT_H


#include "list.h"


#include "../record-int.h"



/* Liste de correspondances établies entre attributs et binaire (instance) */
struct _GRecordList
{
    GMatchRecord parent;                    /* A laisser en premier        */

    vmpa2t pos;                             /* Début de zone               */

    GMatchRecord **children;                /* Sous-correspondances        */
    size_t count;                           /* Taille de cette série       */

};

/* Liste de correspondances établies entre attributs et binaire (classe) */
struct _GRecordListClass
{
    GMatchRecordClass parent;               /* A laisser en premier        */

};


/* Met en place une série de correspondances attribut/binaire. */
bool g_record_list_create(GRecordList *, GKaitaiAttribute *, GBinContent *, const vmpa2t *);



#endif  /* _PLUGINS_KAITAI_RECORDS_LIST_INT_H */
