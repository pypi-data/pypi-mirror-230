
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkbufferdisplay-int.h - prototypes internes pour l'affichage de tampons de lignes
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#ifndef _GTK_BUFFERDISPLAY_INT_H
#define _GTK_BUFFERDISPLAY_INT_H


#include "gtkbufferdisplay.h"


#include "gtkdisplaypanel-int.h"



/* Réagit à un déplacement de curseur. */
typedef bool (* notify_caret_relocation_fc) (GtkBufferDisplay *, const GdkRectangle *);


/* Composant d'affichage de tampon de lignes (instance) */
struct _GtkBufferDisplay
{
    GtkDisplayPanel parent;                 /* A laisser en premier        */

    GBufferView *view;                      /* Vue sur le contenu affiché  */

    cairo_rectangle_int_t caret;            /* Emplacement du curseur #1   */
    GLineCursor *cursor;                    /* Emplacement du curseur #2   */
    guint caret_timer;                      /* Identifiant du chronomètre  */
    bool show_caret;                        /* Bascule entre les affichages*/

    GtkBuilder *builder;                    /* Constructeur à manipuler    */
    GtkWidget *bar;                         /* Barre d'outils intégrée     */

};

/* Composant d'affichage de tampon de lignes (classe) */
struct _GtkBufferDisplayClass
{
    GtkDisplayPanelClass parent;            /* A laisser en premier        */

    notify_caret_relocation_fc notify_caret;/* Accompagne un déplacement   */

    /* Signaux */

    void (* reach_limit) (GtkBufferDisplay *, GdkScrollDirection);

    void (* prepare_collapsing) (GtkBufferDisplay *, gboolean);

};



#endif  /* _GTK_BUFFERDISPLAY_INT_H */
