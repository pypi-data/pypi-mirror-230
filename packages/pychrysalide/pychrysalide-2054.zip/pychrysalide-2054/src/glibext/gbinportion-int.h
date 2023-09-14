
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binportion.h - prototypes pour la définition interne des portions de binaire
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


#ifndef _GLIBEXT_BINPORTION_INT_H
#define _GLIBEXT_BINPORTION_INT_H


#include "gbinportion.h"



/* Portion de données binaires quelconques (instance) */
struct _GBinPortion
{
    GObject parent;                         /* A laisser en premier        */

    char *code;                             /* Code de la couleur de fond  */

#ifdef INCLUDE_GTK_SUPPORT
    cairo_surface_t *icon;                  /* Image de représentation     */
#endif

    char *desc;                             /* Désignation humaine         */
    char **text;                            /* Lignes brutes à représenter */
    size_t lcount;                          /* Quantité de ces lignes      */

    mrange_t range;                         /* Emplacement dans le code    */
    bool continued;                         /* Suite d'une découpe ?       */

    PortionAccessRights rights;             /* Droits d'accès              */

    GBinPortion **subs;                     /* Portions incluses           */
    size_t count;                           /* Quantité d'inclusions       */

};

/* Portion de données binaires quelconques (classe) */
struct _GBinPortionClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _GLIBEXT_BINPORTION_INT_H */
