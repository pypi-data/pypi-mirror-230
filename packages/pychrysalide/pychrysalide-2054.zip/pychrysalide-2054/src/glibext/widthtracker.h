
/* Chrysalide - Outil d'analyse de fichiers binaires
 * widthtracker.h - prototypes pour le suivi des largeurs associées à un ensemble de lignes
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


#ifndef _GLIBEXT_WIDTHTRACKER_H
#define _GLIBEXT_WIDTHTRACKER_H


#include <glib-object.h>
#include <stdbool.h>


#include "delayed.h"
#include "gdisplayoptions.h"




/* Mémorisation des largeurs pour un groupe de lignes */
typedef struct _line_width_summary
{
    gint max_widths[10/*BLC_COUNT*/];             /* Taille cachée des colonnes  */
    gint merged_width;                      /* Largeur cumulée avant fusion*/

} line_width_summary;



/* ---------------------------- RASSEMBLEMENT DE MESURES ---------------------------- */


/* gbuffercache.h : Tampon pour gestion de lignes optimisée (instance) */
typedef struct _GBufferCache GBufferCache;

/* ../gtkext/gtkstatusstack.h : Abstration d'une gestion de barre de statut (instance) */
typedef struct _GtkStatusStack GtkStatusStack;


#define G_TYPE_WIDTH_TRACKER            (g_width_tracker_get_type())
#define G_WIDTH_TRACKER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_WIDTH_TRACKER, GWidthTracker))
#define G_WIDTH_TRACKER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_WIDTH_TRACKER, GWidthTrackerClass))
#define G_IS_WIDTH_TRACKER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_WIDTH_TRACKER))
#define G_IS_WIDTH_TRACKER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_WIDTH_TRACKER))
#define G_WIDTH_TRACKER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_WIDTH_TRACKER, GWidthTrackerClass))


/* Gestionnaire de largeurs associées aux lignes (instance) */
typedef struct _GWidthTracker GWidthTracker;

/* Gestionnaire de largeurs associées aux lignes (classe) */
typedef struct _GWidthTrackerClass GWidthTrackerClass;


/* Détermine le type du gestionnaire de largeurs associées aux lignes. */
GType g_width_tracker_get_type(void);

/* Crée un nouveau suivi de largeurs au sein de lignes. */
GWidthTracker *g_width_tracker_new(GBufferCache *, size_t, size_t);

/* Crée un nouveau suivi de largeurs au sein de lignes. */
GWidthTracker *g_width_tracker_new_restricted(const GWidthTracker *, size_t, size_t);

/* Indique le nombre de colonnes prises en compte. */
size_t g_width_tracker_count_columns(const GWidthTracker *);

/* Indique la largeur minimale pour une colonne donnée. */
gint g_width_tracker_get_column_min_width(GWidthTracker *, size_t);

/* Impose une largeur minimale pour une colonne donnée. */
void g_width_tracker_set_column_min_width(GWidthTracker *, size_t, gint);

/* Prend acte d'un changement sur une ligne pour les largeurs. */
void g_width_tracker_update(GWidthTracker *, size_t);

/* Prend acte de l'ajout de lignes pour les largeurs. */
void g_width_tracker_update_added(GWidthTracker *, size_t, size_t);

/* Prend acte de la suppression de lignes pour les largeurs. */
void g_width_tracker_update_deleted(GWidthTracker *, size_t, size_t);

/* Calcule les largeurs requises par un ensemble de lignes. */
void g_width_tracker_build_initial_cache(GWidthTracker *, wgroup_id_t, GtkStatusStack *);

/* Fournit la largeur requise par une visualisation. */
gint g_width_tracker_get_width(GWidthTracker *, const GDisplayOptions *);

/* Fournit la largeur requise pour dépasser les marges gauches. */
gint g_width_tracker_get_margin(GWidthTracker *, const GDisplayOptions *);

/* Indique la largeur locale d'une colonne donnée. */
gint g_width_tracker_get_local_column_width(GWidthTracker *, size_t, size_t, size_t);



#endif  /* _GLIBEXT_WIDTHTRACKER_H */
