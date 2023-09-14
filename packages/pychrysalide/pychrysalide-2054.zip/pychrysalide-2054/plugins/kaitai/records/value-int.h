
/* Chrysalide - Outil d'analyse de fichiers binaires
 * value-int.h - prototypes internes pour la conservation d'une instance virtuelle
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


#ifndef _PLUGINS_KAITAI_RECORDS_VALUE_INT_H
#define _PLUGINS_KAITAI_RECORDS_VALUE_INT_H


#include "value.h"


#include "../record-int.h"



/* Valeur calculée selon des correspondances parallèles (instance) */
struct _GRecordValue
{
    GMatchRecord parent;                    /* A laisser en premier        */

    kaitai_scope_t locals;                  /* Sauvegarde de contexte      */

};

/* Valeur calculée selon des correspondances parallèles (classe) */
struct _GRecordValueClass
{
    GMatchRecordClass parent;               /* A laisser en premier        */

};


/* Met en place une valeur calculée selon des correspondances. */
bool g_record_value_create(GRecordValue *, GKaitaiInstance *, const kaitai_scope_t *);



#endif  /* _PLUGINS_KAITAI_RECORDS_VALUE_INT_H */
