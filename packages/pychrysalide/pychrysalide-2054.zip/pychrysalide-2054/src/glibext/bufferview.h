
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bufferview.h - prototypes pour l'affichage d'une vue particulière d'un tampon de lignes
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


#ifndef _GLIBEXT_BUFFERVIEW_H
#define _GLIBEXT_BUFFERVIEW_H


#include <glib-object.h>


#include "buffercache.h"
#include "gdisplayoptions.h"



#define G_TYPE_BUFFER_VIEW              (g_buffer_view_get_type())
#define G_BUFFER_VIEW(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BUFFER_VIEW, GBufferView))
#define G_BUFFER_VIEW_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BUFFER_VIEW, GBufferViewClass))
#define G_IS_BUFFER_VIEW(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BUFFER_VIEW))
#define G_IS_BUFFER_VIEW_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BUFFER_VIEW))
#define G_BUFFER_VIEW_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BUFFER_VIEW, GBufferViewClass))


/* Vue d'un tampon pour code désassemblé (instance) */
typedef struct _GBufferView GBufferView;

/* Vue d'un tampon pour code désassemblé (classe) */
typedef struct _GBufferViewClass GBufferViewClass;


/* Détermine le type de la vue d'un tampon pour lignes générées. */
GType g_buffer_view_get_type(void);

/* Crée une nouvelle vue d'un tampon pour lignes générées. */
GBufferView *g_buffer_view_new(GBufferCache *, segcnt_list *);

/* Fournit le tampon de code lié à un visualisateur donné. */
GBufferCache *g_buffer_view_get_cache(const GBufferView *);

/* Restreint le champ d'application de l'affichage. */
void g_buffer_view_restrict(GBufferView *, GLineCursor *, GLineCursor *);

/* Indique le champ d'application de l'affichage. */
bool g_buffer_view_get_restrictions(const GBufferView *, GLineCursor **, GLineCursor **);



/* Fournit la largeur requise par une visualisation. */
gint g_buffer_view_get_width(GBufferView *, const GDisplayOptions *);

/* Fournit la largeur requise pour dépasser les marges gauches. */
gint g_buffer_view_get_margin(GBufferView *, const GDisplayOptions *);

/* Fournit la hauteur requise par une visualisation. */
gint g_buffer_view_get_height(const GBufferView *);





/* Calcule la position idéale de curseur pour un point donné. */
bool g_buffer_view_compute_caret_full(GBufferView *, gint, gint, const GDisplayOptions *, cairo_rectangle_int_t *, GLineCursor **);

/* Déplace le curseur au sein d'une vue de tampon. */
bool g_buffer_view_move_caret(GBufferView *, bool, GdkScrollDirection, const GDisplayOptions *, cairo_rectangle_int_t *, GLineCursor **);



/* Trouve le créateur à l'origine d'un emplacement donné. */
GObject *g_buffer_view_find_creator(GBufferView *, gint, gint, const GDisplayOptions *);



/* Supprime toute mise en évidence de segments. */
bool g_buffer_view_unhighlight_segments(GBufferView *);

/* Surligne tous les segments similaires à celui sous la souris. */
bool g_buffer_view_highlight_segments(GBufferView *, gint, gint, const GDisplayOptions *);

/* Imprime la visualisation du tampon de lignes quelconques. */
void g_buffer_view_draw(const GBufferView *, cairo_t *, gint, const cairo_rectangle_int_t *, const GDisplayOptions *, gint *, double, bool);






/* Indique la position d'affichage d'une adresse donnée. */
bool g_buffer_view_get_cursor_coordinates(GBufferView *, const GLineCursor *, bool, gint *, gint *);





#endif  /* _GLIBEXT_BUFFERVIEW_H */
