
/* Chrysalide - Outil d'analyse de fichiers binaires
 * buffercache.h - prototypes pour l'affichage à la demande d'un ensemble de lignes
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


#ifndef _GLIBEXT_BUFFERCACHE_H
#define _GLIBEXT_BUFFERCACHE_H


#include <glib-object.h>
#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gdk/gdk.h>
#endif


#include "gdisplayoptions.h"
#include "linegen.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "widthtracker.h"
#endif



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


#define G_TYPE_BUFFER_CACHE            g_buffer_cache_get_type()
#define G_BUFFER_CACHE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BUFFER_CACHE, GBufferCache))
#define G_BUFFER_CACHE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BUFFER_CACHE, GBufferCacheClass))
#define G_IS_BUFFER_CACHE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BUFFER_CACHE))
#define G_IS_BUFFER_CACHE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BUFFER_CACHE))
#define G_BUFFER_CACHE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BUFFER_CACHE, GBufferCacheClass))


/* Tampon pour gestion de lignes optimisée (instance) */
typedef struct _GBufferCache GBufferCache;

/* Tampon pour gestion de lignes optimisée (classe) */
typedef struct _GBufferCacheClass GBufferCacheClass;


/* Détermine le type du composant de tampon pour gestion de lignes optimisée. */
GType g_buffer_cache_get_type(void);

/* Crée un nouveau composant de tampon pour code désassemblé. */
GBufferCache *g_buffer_cache_new(GBinContent *, size_t, size_t);

/* Indique l'éventuel contenu binaire associé au cache. */
GBinContent *g_buffer_cache_get_content(const GBufferCache *);

/* Fournit la hauteur d'impression d'une ligne visualisée. */
gint g_buffer_cache_get_line_height(const GBufferCache *);

/* Fournit la taille réservée pour la marge gauche. */
gint g_buffer_cache_get_left_margin(const GBufferCache *);

/* Fournit la position de départ pour l'impression de texte. */
gint g_buffer_cache_get_text_position(const GBufferCache *);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit un lien vers la structure de suivi de largeurs. */
GWidthTracker *g_buffer_cache_get_width_tracker(const GBufferCache *);

#endif

/*  Met à disposition un encadrement des accès aux lignes. */
void g_buffer_cache_lock_unlock(GBufferCache *, bool, bool);


#define g_buffer_cache_wlock(cache) g_buffer_cache_lock_unlock(cache, true, true);
#define g_buffer_cache_wunlock(cache) g_buffer_cache_lock_unlock(cache, true, false);

#define g_buffer_cache_rlock(cache) g_buffer_cache_lock_unlock(cache, false, true);
#define g_buffer_cache_runlock(cache) g_buffer_cache_lock_unlock(cache, false, false);


/* Compte le nombre de lignes rassemblées dans un tampon. */
size_t g_buffer_cache_count_lines(GBufferCache *);

/* Insère un générateur dans des lignes à une position donnée. */
void g_buffer_cache_insert_at(GBufferCache *, size_t, GLineGenerator *, BufferLineFlags, bool, bool);

/* Retire une ligne du tampon. */
void g_buffer_cache_delete_at(GBufferCache *, size_t);

/* Retire un type de générateur de lignes. */
GLineGenerator *g_buffer_cache_delete_type_at(GBufferCache *, size_t, GType, bool, bool);

/* Ajoute en fin de tampon un générateur de lignes. */
void g_buffer_cache_append(GBufferCache *, GLineGenerator *, BufferLineFlags);

/* Etend un tampon avec un générateur de lignes unique. */
void g_buffer_cache_extend_with(GBufferCache *, size_t, GLineGenerator *);

/* Réduit le tampon à une quantité de lignes précise. */
void g_buffer_cache_truncate(GBufferCache *, size_t);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position de ligne. */
void g_buffer_cache_get_line_cursor(GBufferCache *, size_t, gint, GLineCursor **);

#endif

/* Ajoute une propriété particulière à une ligne. */
void g_buffer_cache_add_line_flag(GBufferCache *, size_t, BufferLineFlags);

/* Détermine l'ensemble des propriétés attachées à une ligne. */
BufferLineFlags g_buffer_cache_get_line_flags(GBufferCache *, size_t);

/* Retire une propriété particulière attachée à une ligne. */
void g_buffer_cache_remove_line_flag(GBufferCache *, size_t, BufferLineFlags);

/* Avance autant que possible vers une ligne idéale. */
size_t g_buffer_cache_look_for_flag(GBufferCache *, size_t, BufferLineFlags);

/* Force la mise à jour du contenu d'une ligne donnée. */
void g_buffer_cache_refresh_line(GBufferCache *, size_t);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve une ligne au sein d'un tampon avec un indice. */
GBufferLine *g_buffer_cache_find_line_by_index(GBufferCache *, size_t);

/* Fait remonter les largeurs requises par une ligne donnée. */
void g_buffer_cache_collect_widths(GBufferCache *, size_t, size_t, size_t, gint *, gint *);

/* Imprime une partie choisie du tampon contenant des lignes. */
void g_buffer_cache_draw(const GBufferCache *, cairo_t *, size_t, size_t, const cairo_rectangle_int_t *, const GDisplayOptions *, const gint *, const segcnt_list *);

#endif

/* Indique l'indice correspondant à une adresse donnée. */
size_t _g_buffer_cache_find_index_by_cursor(GBufferCache *, const GLineCursor *, bool, size_t, size_t);

/* Indique l'indice correspondant à une adresse donnée. */
size_t g_buffer_cache_find_index_by_cursor(GBufferCache *, const GLineCursor *, bool);

#ifdef INCLUDE_GTK_SUPPORT

/* Indique la position d'affichage d'une adresse donnée. */
bool g_buffer_cache_get_cursor_coordinates(GBufferCache *, const GLineCursor *, size_t, size_t, bool, gint *, gint *);

#endif



#endif  /* _GLIBEXT_BUFFERCACHE_H */
