
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkbufferdisplay.h - prototypes pour l'affichage de tampons de lignes
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


#ifndef _GTKEXT_GTKBUFFER_DISPLAY_H
#define _GTKEXT_GTKBUFFER_DISPLAY_H


#include <glib-object.h>
#include <gtk/gtk.h>


#include "../glibext/bufferview.h"



#define GTK_TYPE_BUFFER_DISPLAY             (gtk_buffer_display_get_type())
#define GTK_BUFFER_DISPLAY(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_BUFFER_DISPLAY, GtkBufferDisplay))
#define GTK_BUFFER_DISPLAY_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_BUFFER_DISPLAY, GtkBufferDisplayClass))
#define GTK_IS_BUFFER_DISPLAY(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_BUFFER_DISPLAY))
#define GTK_IS_BUFFER_DISPLAY_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_BUFFER_DISPLAY))
#define GTK_BUFFER_DISPLAY_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_BUFFER_VIEW, GtkBufferDisplayClass))


/* Composant d'affichage de tampon de lignes (instance) */
typedef struct _GtkBufferDisplay GtkBufferDisplay;

/* Composant d'affichage de tampon de lignes (classe) */
typedef struct _GtkBufferDisplayClass GtkBufferDisplayClass;


/* Détermine le type du composant d'affichage de tampon de lignes. */
GType gtk_buffer_display_get_type(void);

/* Fournit la vue associée au tampon de lignes courant. */
GBufferView *gtk_buffer_display_get_view(const GtkBufferDisplay *);



/* ------------------------------ ANIMATION DU CURSEUR ------------------------------ */


/* Détermine si une position est comprise dans l'affichage. */
bool gtk_buffer_display_contain_cursor(const GtkBufferDisplay *, const GLineCursor *);

/* Déplace le curseur à un emplacement en extrémité. */
bool gtk_buffer_display_move_caret_to(GtkBufferDisplay *, bool, gint *);



/* ------------------------- INCLUSION D'UNE BARRE D'OUTILS ------------------------- */


/* Ajoute une nouvelle barre d'outils pour bloc au composant. */
void gtk_buffer_display_add_block_bar(GtkBufferDisplay *);



#endif  /* _GTKEXT_GTKBUFFER_DISPLAY_H */
