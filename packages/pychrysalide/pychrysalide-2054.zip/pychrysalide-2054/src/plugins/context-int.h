
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context-int.h - prototypes pour les structures internes des instances de greffon
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _FORMAT_PLUGINS_CONTEXT_INT_H
#define _FORMAT_PLUGINS_CONTEXT_INT_H


#include <glib-object.h>



/* Instance de greffon pour Chrysalide (instance) */
struct _GPluginContext
{
    GObject parent;                         /* A laisser en premier        */

};


/* Instance de greffon pour Chrysalide (classe) */
struct _GPluginContextClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _FORMAT_PLUGINS_CONTEXT_INT_H */
