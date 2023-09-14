
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array-int.h - prototypes pour les données associées à un flux de données Kaitai
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


#ifndef PLUGINS_KAITAI_ARRAY_INT_H
#define PLUGINS_KAITAI_ARRAY_INT_H


#include "array.h"



/* Tableau rassemblant des éléments divers (instance) */
struct _GKaitaiArray
{
    GObject parent;                         /* A laisser en premier        */

    resolved_value_t *items;                /* Eléments du tableau         */
    size_t count;                           /* Quantité de ces éléments    */

};

/* Tableau rassemblant des éléments divers (classe) */
struct _GKaitaiArrayClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* PLUGINS_KAITAI_ARRAY_INT_H */
