
/* Chrysalide - Outil d'analyse de fichiers binaires
 * support.h - prototypes pour la recherche des chemins d'accès aux fichiers
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _GTKEXT_SUPPORT_H
#define _GTKEXT_SUPPORT_H


#include <gtk/gtk.h>



/* Construit une image à partir d'un nom de fichier. */
GtkWidget *get_image_from_file(const char *);

/* Construit un tampon d'image à partir d'un nom de fichier. */
GdkPixbuf *get_pixbuf_from_file(const char *);



#endif  /* _GTKEXT_SUPPORT_H */
