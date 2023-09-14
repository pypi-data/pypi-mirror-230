
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named-int.h - définitions internes propres aux manipulations de composants nommés
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _GLIBEXT_NAMED_INT_H
#define _GLIBEXT_NAMED_INT_H


#include "named.h"



/* Fournit le désignation associée à un composant nommé. */
typedef char * (* get_named_widget_name_fc) (const GNamedWidget *, bool);

/* Fournit le composant associé à un composant nommé. */
typedef GtkWidget * (* get_named_widget_widget_fc) (const GNamedWidget *);


/* Manipulation d'un composant avec ses noms (interface) */
struct _GNamedWidgetIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    get_named_widget_name_fc get_name;      /* Obtention d'un nom (long ?) */
    get_named_widget_widget_fc get_widget;  /* Fourniture du composant     */

};


/* Redéfinition */
typedef GNamedWidgetIface GNamedWidgetInterface;



#endif  /* _GLIBEXT_NAMED_INT_H */
