
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdockable-int.h - définitions internes propres aux éléments acceptés dans les composants de rassemblement
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _GTK_DOCKABLE_INT_H
#define _GTK_DOCKABLE_INT_H


#include "gtkdockable.h"


#include <regex.h>



/* Fournit le nom court du composant encapsulable. */
typedef char * (* get_dockable_name_fc) (const GtkDockable *);

/* Fournit le nom court du composant encapsulable. */
typedef char * (* get_dockable_desc_fc) (const GtkDockable *);

/* Indique si le composant représenté à du contenu à fouiller. */
typedef bool (* can_dockable_search_fc) (const GtkDockable *);

/* Fournit le composant principal à encapsuler au besoin. */
typedef GtkWidget * (* get_dockable_widget_fc) (const GtkDockable *);

/* Démarre l'actualisation du filtrage des paramètres. */
typedef void (* update_filtered_data_fc) (GtkDockable *, const char *);


/* Elément accepté dans les rassemblements (interface) */
struct _GtkDockableIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    get_dockable_name_fc get_name;          /* Nom pour titre              */
    get_dockable_desc_fc get_desc;          /* Description humaine         */
    can_dockable_search_fc can_search;      /* Contenu fouillable ?        */

    get_dockable_widget_fc get_widget;      /* Composant à représenter     */
    update_filtered_data_fc update_filtered;/* Mise à jour du filtrage     */

};


/* Redéfinition */
typedef GtkDockableIface GtkDockableInterface;



#endif  /* _GTK_DOCKABLE_INT_H */
