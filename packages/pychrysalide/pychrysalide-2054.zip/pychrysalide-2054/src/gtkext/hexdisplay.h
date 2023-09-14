
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hexdisplay.h - prototypes pour l'affichage d'un contenu binaire sous forme hexadécimale
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GTKEXT_HEXDISPLAY_H
#define _GTKEXT_HEXDISPLAY_H


#include <glib-object.h>
#include <gtk/gtk.h>


#include "../analysis/content.h"



#define GTK_TYPE_HEX_DISPLAY            (gtk_hex_display_get_type())
#define GTK_HEX_DISPLAY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_HEX_DISPLAY, GtkHexDisplay))
#define GTK_HEX_DISPLAY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_HEX_DISPLAY, GtkHexDisplayClass))
#define GTK_IS_HEX_DISPLAY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_HEX_DISPLAY))
#define GTK_IS_HEX_DISPLAY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_HEX_DISPLAY))
#define GTK_HEX_DISPLAY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_HEX_DISPLAY, GtkHexDisplayClass))


/* Composant d'affichage de contenu sous forme hexadécimale (instance) */
typedef struct _GtkHexDisplay GtkHexDisplay;

/* Composant d'affichage de contenu sous forme hexadécimale (classe) */
typedef struct _GtkHexDisplayClass GtkHexDisplayClass;


/* Détermine le type du composant d'affichage sous forme hexadécimale. */
GType gtk_hex_display_get_type(void);

/* Crée un nouveau composant pour l'affichage sous forme hexa. */
GtkWidget *gtk_hex_display_new(GBinContent *);



#endif  /* _GTKEXT_HEXDISPLAY_H */
