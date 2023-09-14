
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item-int.h - prototypes pour les définitions internes liées aux éléments réactifs de l'éditeur
 *
 * Copyright (C) 2010-2020 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_ITEM_INT_H
#define _GUI_ITEM_INT_H


#include "item.h"


#include <gtk/gtkwidget.h>



/* Fournit le nom interne attribué à l'élément réactif. */
typedef char * (* get_item_key_fc) (const GEditorItemClass *);

/* Fournit le composant GTK associé à l'élément réactif. */
typedef GtkWidget * (* get_item_widget_fc)  (const GEditorItem *);

/* Réagit à un changement de contenu chargé en cours d'analyse. */
typedef void (* change_item_content_fc) (GEditorItem *, GLoadedContent *, GLoadedContent *);

/* Réagit à un changement de vue du contenu en cours d'analyse. */
typedef void (* change_item_view_fc) (GEditorItem *, GLoadedPanel *, GLoadedPanel *);

/* Réagit à une modification de la vue du contenu analysé. */
typedef void (* update_item_view_fc) (GEditorItem *, GLoadedPanel *);

/* Suit les changements de position dans du code d'assembleur. */
typedef void (* track_cursor_in_view_fc) (GEditorItem *, GLoadedPanel *, const GLineCursor *);

/* Concentre l'attention de l'ensemble sur une adresse donnée. */
typedef void (* focus_cursor_fc) (GEditorItem *, GLoadedContent *, const GLineCursor *);

/* Lance une actualisation relative à l'étendue du projet. */
typedef void (* update_project_fc) (GEditorItem *, GStudyProject *);


/* Elément réactif quelconque de l'éditeur (instance) */
struct _GEditorItem
{
    GObject parent;                         /* A laisser en premier        */

};


/* Elément réactif quelconque de l'éditeur (classe) */
struct _GEditorItemClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_item_key_fc get_key;                /* Obtention d'un nom clef     */
    get_item_widget_fc get_widget;          /* Fourniture du composant     */

    change_item_content_fc change_content;  /* Changement de contenu       */
    change_item_view_fc change_view;        /* Rechargement dû à une vue   */
    update_item_view_fc update_view;        /* Rechargement dû à évolutions*/

    track_cursor_in_view_fc track_cursor;   /* Suivi des positions         */
    focus_cursor_fc focus_cursor;           /* Prête attention à une addr. */

    update_project_fc update_project;       /* Actualisation des binaires  */

};



#endif  /* _GUI_ITEM_INT_H */
