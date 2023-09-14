
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bufferline.h - prototypes pour la représentation de fragments de texte en ligne
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _GLIBEXT_BUFFERLINE_H
#define _GLIBEXT_BUFFERLINE_H


#include <glib-object.h>
#include <stdbool.h>


#include "gdisplayoptions.h"
#include "linesegment.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "widthtracker.h"
#endif
#include "../analysis/content.h"
#include "../arch/vmpa.h"



#define G_TYPE_BUFFER_LINE            g_buffer_line_get_type()
#define G_BUFFER_LINE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BUFFER_LINE, GBufferLine))
#define G_BUFFER_LINE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BUFFER_LINE, GBufferLineClass))
#define G_IS_BUFFER_LINE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BUFFER_LINE))
#define G_IS_BUFFER_LINE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BUFFER_LINE))
#define G_BUFFER_LINE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BUFFER_LINE, GBufferLineClass))


/* Représentation de fragments de texte en ligne (instance) */
typedef struct _GBufferLine GBufferLine;

/* Représentation de fragments de texte en ligne (classe) */
typedef struct _GBufferLineClass GBufferLineClass;


/* Confort pour l'insertion de texte */
#define SL(str) str, strlen(str)

/* Espace entre les colonnes */
#define COL_MARGIN 23


/* Propriétés particulières supplémentaires */
typedef enum _BufferLineFlags
{
    BLF_NONE            = 0 << 0,           /* Aucune                      */
    BLF_HAS_CODE        = 1 << 0,           /* La ligne contient du code   */
    BLF_IS_LABEL        = 1 << 1,           /* Etiquette pour symbole      */
    BLF_ENTRYPOINT      = 1 << 2,           /* Représentation d'une entrée */
    BLF_BOOKMARK        = 1 << 3,           /* Signet associé              */
    BLF_WIDTH_MANAGER   = 1 << 4,           /* Début de groupe des largeurs*/

    BLF_ALL             = ((1 << 5) - 1)

} BufferLineFlags;


/* Détermine le type de la représentation de fragments de texte en ligne. */
GType g_buffer_line_get_type(void);

/* Crée une nouvelle représentation de fragments de texte. */
GBufferLine *g_buffer_line_new(size_t);

/* Construit le tronc commun d'une ligne autour de sa position. */
void g_buffer_line_fill_phys(GBufferLine *, size_t, MemoryDataSize, const vmpa2t *);

/* Construit le tronc commun d'une ligne autour de sa position. */
void g_buffer_line_fill_virt(GBufferLine *, size_t, MemoryDataSize, const vmpa2t *);

/* Construit le tronc commun d'une ligne autour de son contenu. */
void g_buffer_line_fill_content(GBufferLine *, size_t, const GBinContent *, const mrange_t *, phys_t);

/* Recherche le premier créateur enregistré dans des segments. */
GObject *g_buffer_line_find_first_segment_creator(const GBufferLine *, size_t);

/* Ajoute du texte à formater dans une ligne donnée. */
void g_buffer_line_append_text(GBufferLine *, size_t, const char *, size_t, RenderingTagType, GObject *);

/* Remplace du texte dans une ligne donnée. */
bool g_buffer_line_replace_text(GBufferLine *, const GObject *, const char *, size_t);

/* Indique si du texte est présent dans une ligne de tampon. */
bool g_buffer_line_has_text(const GBufferLine *, size_t, size_t);

/* Donne le texte représenté par une ligne de tampon. */
char *g_buffer_line_get_text(const GBufferLine *, size_t, size_t, bool);

/* Supprime du texte représenté par une ligne de tampon. */
void g_buffer_line_delete_text(GBufferLine *, size_t, size_t);

/* Fournit la colonne à partir de laquelle une fusion opère. */
size_t g_buffer_line_get_merge_start(const GBufferLine *);

/* Définit la colonne à partir de laquelle la fusion opère. */
void g_buffer_line_start_merge_at(GBufferLine *, size_t);

/* Ajoute une propriété particulière à une ligne donnée. */
void g_buffer_line_add_flag(GBufferLine *, BufferLineFlags);

/* Renseigne sur les propriétés particulières liées à une ligne. */
BufferLineFlags g_buffer_line_get_flags(const GBufferLine *);

/* Retire une propriété particulière à une ligne donnée. */
void g_buffer_line_remove_flag(GBufferLine *, BufferLineFlags);

/* Exporte la ligne de texte représentée. */
void g_buffer_line_export(GBufferLine *, buffer_export_context *, BufferExportType, const GDisplayOptions *);



/* ----------------------- MANIPULATION DES LARGEURS REQUISES ----------------------- */


/* Identification d'un contenu de colonne */
typedef struct _col_coord_t
{
    size_t column;                          /* Colonne concernée           */
    size_t index;                           /* Indice d'insertion          */

} col_coord_t;


#ifdef INCLUDE_GTK_SUPPORT

/* Fait remonter les largeurs requises par une ligne donnée. */
void g_buffer_line_collect_widths(const GBufferLine *, size_t, size_t, gint *, gint *);

/* Fournit le segment présent à une position donnée. */
line_segment *g_buffer_line_get_segment_from_coord(const GBufferLine *, const col_coord_t *);

/* Fournit les coordonnées correspondant à une abscisse donnée. */
bool g_buffer_line_get_coord_at(const GBufferLine *, size_t, GWidthTracker *, const GDisplayOptions *, gint *, gint *, GdkScrollDirection, bool, col_coord_t *);

/* Donne le segment présent à une abscisse donnée. */
line_segment *g_buffer_line_get_segment_at(const GBufferLine *, size_t, GWidthTracker *, const GDisplayOptions *, gint *, gint *, GdkScrollDirection, bool);

/* Donne le créateur présent à une abscisse donnée. */
GObject *g_buffer_line_get_creator_at(const GBufferLine *, size_t, GWidthTracker *, const GDisplayOptions *, gint *, gint *, GdkScrollDirection, bool);

/* Fournit des coordonnées voisines selon une direction donnée. */
bool g_buffer_line_find_near_coord(const GBufferLine *, size_t, col_coord_t *, GWidthTracker *, const GDisplayOptions *, GdkScrollDirection, gint *);

/* Imprime la ligne de texte représentée. */
void g_buffer_line_draw(GBufferLine *, size_t, cairo_t *, gint, gint, GWidthTracker *, const GDisplayOptions *, const segcnt_list *);

#endif



#endif  /* _GLIBEXT_BUFFERLINE_H */
