
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linecolumn.h - prototypes pour le regroupement des segments de texte par colonnes
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


#ifndef _GLIBEXT_LINECOLUMN_H
#define _GLIBEXT_LINECOLUMN_H


#include <stdbool.h>
#include <glib-object.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gdk/gdk.h>
#endif


#include "linesegment.h"



/* Informations sur le contenu d'une colonne */
typedef struct _line_column line_column;


/* Informations sur le contenu d'une colonne */
struct _line_column
{
    line_segment **segments;                /* Liste des segments contenus */
    size_t count;                           /* Taille de cette liste       */

#ifdef INCLUDE_GTK_SUPPORT
    int max_width;                          /* Largeur max. de l'espace    */
#endif

};


/* Initialise une colonne de ligne. */
void init_line_column(line_column *);

/* Réinitialise une colonne de ligne. */
void reset_line_column(line_column *);

#ifdef INCLUDE_GTK_SUPPORT

/* Recalcule la largeur d'une colonne de segments. */
void refresh_line_column_width(line_column *);

/* Fournit la quantité de pixels requise pour l'impression. */
gint get_column_width(const line_column *);

#endif

/* Ajoute un fragment de texte à une colonne de ligne. */
size_t append_text_to_line_column(line_column *, const char *, size_t, RenderingTagType);

/* Remplace un fragment de texte dans une colonne de ligne. */
void replace_text_in_line_column(line_column *, size_t, const char *, size_t);

#ifdef INCLUDE_GTK_SUPPORT

/* Indique l'indice du premier contenu de la colonne. */
bool get_line_column_first_content_index(const line_column *, size_t *);

/* Indique l'indice du dernier contenu de la colonne. */
bool get_line_column_last_content_index(const line_column *, size_t *);

/* Fournit le segment voisin d'un autre segment identifié. */
bool find_near_segment(const line_column *, size_t *, GdkScrollDirection);

/* Indique l'indice du contenu de colonne à une abscisse donnée. */
bool get_line_column_content_index_at(const line_column *, gint *, GdkScrollDirection, gint *, size_t *);

/* Donne le segment d'une colonne présent à un indice donné. */
line_segment *get_line_column_content_from_index(const line_column *, size_t);

/* Imprime le contenu d'une colonne de ligne de texte. */
void draw_line_column_segments(const line_column *, cairo_t *, gint, gint, const segcnt_list *);

#endif

/* Donne le texte représenté par une colonne de ligne de texte. */
char *get_line_column_text(const line_column *, bool);

/* Exporte la ligne de texte représentée. */
void export_line_column_segments(const line_column *, buffer_export_context *, BufferExportType, int);



#endif  /* _GLIBEXT_LINECOLUMN_H */
