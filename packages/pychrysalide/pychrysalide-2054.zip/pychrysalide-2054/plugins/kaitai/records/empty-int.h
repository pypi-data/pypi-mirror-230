
/* Chrysalide - Outil d'analyse de fichiers binaires
 * empty-int.h - prototypes internes pour la notification d'une absence de correspondance attendue
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


#ifndef _PLUGINS_KAITAI_RECORDS_EMPTY_INT_H
#define _PLUGINS_KAITAI_RECORDS_EMPTY_INT_H


#include "empty.h"


#include "../record-int.h"



/* Marque d'une zone de correspondance vide (instance) */
struct _GRecordEmpty
{
    GMatchRecord parent;                    /* A laisser en premier        */

    vmpa2t pos;                             /* Début d'une zone vide       */

};

/* Marque d'une zone de correspondance vide (classe) */
struct _GRecordEmptyClass
{
    GMatchRecordClass parent;               /* A laisser en premier        */

};


/* Met en place une zone de correspondance vide. */
bool g_record_empty_create(GRecordEmpty *, GKaitaiParser *, GBinContent *, const vmpa2t *);



#endif  /* _PLUGINS_KAITAI_RECORDS_EMPTY_INT_H */
