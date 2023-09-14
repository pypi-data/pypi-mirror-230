
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkbinarystrip.h - prototypes pour l'affichage d'un binaire sous forme de bande
 *
 * Copyright (C) 2013-2018 Cyrille Bagard
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


#ifndef _GTKEXT_BINARYSTRIP_H
#define _GTKEXT_BINARYSTRIP_H


#include <glib-object.h>
#include <gtk/gtk.h>


#include "../analysis/binary.h"



#define GTK_TYPE_BINARY_STRIP                  (gtk_binary_strip_get_type())
#define GTK_BINARY_STRIP(obj)                  (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_BINARY_STRIP, GtkBinaryStrip))
#define GTK_BINARY_STRIP_CLASS(klass)          (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_BINARY_STRIP, GtkBinaryStripClass))
#define GTK_IS_BINARY_STRIP(obj)               (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_BINARY_STRIP))
#define GTK_IS_BINARY_STRIP_CLASS(klass)       (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_BINARY_STRIP))
#define GTK_BINARY_STRIP_GET_CLASS(obj)        (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_BINARY_STRIP, GtkBinaryStripClass))


/* Affichage d'un binaire en bande (instance) */
typedef struct _GtkBinaryStrip GtkBinaryStrip;

/* Affichage d'un binaire en bande (classe) */
typedef struct _GtkBinaryStripClass GtkBinaryStripClass;


/* Détermine le type du composant d'affichage générique. */
GType gtk_binary_strip_get_type(void);

/* Crée un nouveau composant pour l'affichage d'une bande. */
GtkWidget *gtk_binary_strip_new(void);

/* Attache un nouveau binaire à la barre de représentation. */
void gtk_binary_strip_attach(GtkBinaryStrip *, GLoadedBinary *);

/* Indique l'adresse physique et virtuelle représentée. */
const vmpa2t *gtk_binary_strip_get_location(const GtkBinaryStrip *);



#endif  /* _GTKEXT_BINARYSTRIP_H */
