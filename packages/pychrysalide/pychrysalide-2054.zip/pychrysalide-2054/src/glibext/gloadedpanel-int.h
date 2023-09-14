
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gloadedpanel-int.h - définitions internes propres à l'affichage de contenus chargés
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _GLIBEXT_GLOADEDPANEL_INT_H
#define _GLIBEXT_GLOADEDPANEL_INT_H


#include "gloadedpanel.h"



/* Définit le contenu associé à un panneau de chargement. */
typedef void (* set_loaded_panel_content_fc) (GLoadedPanel *, GLoadedContent *);

/* Fournit le contenu associé à un panneau de chargement. */
typedef GLoadedContent * (* get_loaded_panel_content_fc) (const GLoadedPanel *);

/* Fournit le position courante dans un panneau de chargement. */
typedef GLineCursor * (* get_loaded_cursor_fc) (const GLoadedPanel *);

/* S'assure qu'un emplacement donné est visible à l'écran. */
typedef void (* scroll_loaded_to_cursor_fc) (GLoadedPanel *, const GLineCursor *, ScrollPositionTweak, bool);

/* Place en cache un rendu destiné à l'aperçu graphique rapide. */
typedef void (* cache_loaded_glance_fc) (GLoadedPanel *, cairo_t *, const GtkAllocation *, double);


/* Intermédiaire pour la génération de lignes (interface) */
struct _GLoadedPanelIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    /* Méthodes virtuelles */

    set_loaded_panel_content_fc set_content;/* Définition du contenu       */
    get_loaded_panel_content_fc get_content;/* Récupération du contenu     */

    get_loaded_cursor_fc get_cursor;        /* Fourniture d'une position   */
    scroll_loaded_to_cursor_fc scroll;      /* Défilement de la vue        */

    cache_loaded_glance_fc cache_glance;    /* Cache de la mignature       */

    /* Signaux */

    void (* move_request) (GLoadedPanel *, const GLineCursor *, gboolean);
    void (* cursor_moved) (GLoadedPanel *, const GLineCursor *);

};


/* Redéfinition */
typedef GLoadedPanelIface GLoadedPanelInterface;



#endif  /* _GLIBEXT_GLOADEDPANEL_INT_H */
