
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkblockdisplay.h - prototypes pour l'affichage d'un fragment de code d'assemblage
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _GTKEXT_GTKBLOCKDISPLAY_H
#define _GTKEXT_GTKBLOCKDISPLAY_H


#include <glib-object.h>
#include <gtk/gtk.h>


#include "../glibext/bufferview.h"



#define GTK_TYPE_BLOCK_DISPLAY            (gtk_block_display_get_type())
#define GTK_BLOCK_DISPLAY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_BLOCK_DISPLAY, GtkBlockDisplay))
#define GTK_BLOCK_DISPLAY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_BLOCK_DISPLAY, GtkBlockDisplayClass))
#define GTK_IS_BLOCK_DISPLAY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_BLOCK_DISPLAY))
#define GTK_IS_BLOCK_DISPLAY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_BLOCK_DISPLAY))
#define GTK_BLOCK_DISPLAY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_BLOCK_DISPLAY, GtkBlockDisplayClass))


/* Composant d'affichage de code d'assembleur (instance) */
typedef struct _GtkBlockDisplay GtkBlockDisplay;

/* Composant d'affichage de code d'assembleur (classe) */
typedef struct _GtkBlockDisplayClass GtkBlockDisplayClass;


/* Détermine le type du composant d'affichage de bloc en langage d'assemblage. */
GType gtk_block_display_get_type(void);

/* Crée un nouveau composant pour l'affichage de bloc en ASM. */
GtkWidget *gtk_block_display_new(GBufferView *);

/* Force un type de vue pour les options de rendu. */
void gtk_block_display_override_view_index(GtkBlockDisplay *, unsigned int);



#endif  /* _GTKEXT_GTKBLOCKDISPLAY_H */
