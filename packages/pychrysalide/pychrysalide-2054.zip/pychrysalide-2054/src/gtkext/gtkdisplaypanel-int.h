
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdisplaypanel-int.h - définitions internes propres à l'affichage de contenus de binaire
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


#ifndef _GTK_DISPLAYPANEL_INT_H
#define _GTK_DISPLAYPANEL_INT_H


#include "gtkdisplaypanel.h"


#include <stdbool.h>
#include <gtk/gtk.h>


#include "../analysis/binary.h"
#include "../glibext/gloadedpanel.h"



/* Amplitude de l'arrondi pour les coins */
#define BORDER_CORNER_RADIUS 10.0


/* Indique les dimensions de travail du composant d'affichage. */
typedef void (* compute_requested_size_fc) (GtkDisplayPanel *, gint *, gint *);

/* Détermine la taille des bonds lors de défilements. */
typedef void (* compute_scroll_inc_fc) (GtkDisplayPanel *, gint, GtkOrientation, gdouble *, gdouble *);

/* Réagit à un défilement chez une barre associée au composant. */
typedef void (* adjust_scroll_value_fc) (GtkDisplayPanel *, GtkAdjustment *, GtkOrientation);

/* Ajuste au besoin la zone affichée pour un curseur. */
typedef void (* prepare_for_cursor_fc) (GtkDisplayPanel *, const GLineCursor *);

/* Indique la position d'affichage d'une adresse donnée. */
typedef bool (* get_coordinates_fc) (const GtkDisplayPanel *, const GLineCursor *, gint *, gint *, ScrollPositionTweak);

/* Fournit l'élément actif lié à la position courante. */
typedef GObject * (* get_active_object_fc) (const GtkDisplayPanel *);

/* Fournit des éléments liés à la position courante dans la vue. */
typedef bool (* get_view_position_fc) (const GtkDisplayPanel *, GBufferLine **, GObject **);

/* Déplace le curseur à un emplacement défini. */
typedef bool (* move_caret_to_fc) (GtkDisplayPanel *, gint, gint);

/* Fournit le position courante dans un panneau de chargement. */
typedef GLineCursor * (* get_cursor_fc) (const GtkDisplayPanel *);

/* Place en cache un rendu destiné à l'aperçu graphique rapide. */
typedef void (* cache_glance_fc) (GtkDisplayPanel *, cairo_t *, const GtkAllocation *, double);

/* Spécifie l'échelle à appliquer à l'affichage du composant. */
typedef void (* apply_scale_fc) (GtkDisplayPanel *, double, double);

/* Marque ou non le composant pour une exportation prochaine. */
typedef void (* prepare_export_fc) (GtkDisplayPanel *, bool);



/* Composant d'affichage générique (instance) */
struct _GtkDisplayPanel
{
    GtkFixed parent;                        /* A laisser en premier        */

    GtkAdjustment *hadjustment;             /* Barre de défilement horiz.  */
    GtkAdjustment *vadjustment;             /* Barre de défilement vert.   */
    GtkScrollablePolicy hscroll_policy;     /* Politique horizontale       */           
    GtkScrollablePolicy vscroll_policy;     /* Politique verticale         */           

    double scale;                           /* Echelle de l'affichage      */

    bool show_border;                       /* Affichage d'une bordure ?   */
    unsigned int view_index;                /* Indice du type de contenu   */
    GDisplayOptions *options;               /* Affichage des colonnes ?    */

    GLoadedBinary *binary;                  /* Binaire à visualiser        */

    bool export;                            /* Exportation du rendu ?      */

};

/* Composant d'affichage générique (classe) */
struct _GtkDisplayPanelClass
{
    GtkFixedClass parent;                   /* A laisser en premier        */

    compute_requested_size_fc compute_size; /* Calcul de la taille requise */
    compute_scroll_inc_fc compute_inc;      /* Calcul des bonds            */
    adjust_scroll_value_fc adjust;          /* Réaction à un défilement    */
    prepare_for_cursor_fc prepare;          /* Préparation de zone affichée*/
    get_coordinates_fc get_coordinates;     /* Conversion adresse <-> pos. */
    get_active_object_fc get_active;        /* Infos sur l'objet actif     */
    move_caret_to_fc move_caret_to;         /* Déplacement du curseur      */

    get_cursor_fc get_cursor;               /* Fourniture d'une position   */
    cache_glance_fc cache_glance;           /* Cache de la mignature       */

    apply_scale_fc scale;                   /* Mise à jour de l'échelle    */

    prepare_export_fc prepare_export;       /* Préparation d'exportation   */

    /* Signaux */

    void (* scaled) (GtkDisplayPanel *, double, double);

};

/* Propriétés propres au composant d'affichage */
typedef enum _ViewPanelProps
{
    VPP_0,
    VPP_HADJUSTMENT,
    VPP_VADJUSTMENT,
    VPP_HSCROLL_POLICY,
    VPP_VSCROLL_POLICY

} ViewPanelProps;


/* Définit un chemin décrivant la bordure autour du panneau. */
void gtk_display_panel_define_border_path(GtkDisplayPanel *, cairo_t *, const GtkAllocation *);

/* Dessine si besoin est une bordure autour du composant. */
void gtk_display_panel_draw_border(GtkDisplayPanel *, cairo_t *);



/* --------------------------- CONVERSIONS DE COORDONNEES --------------------------- */


/* Transcrit les coordonnées à l'écran en coordonnées absolues. */
void gtk_display_panel_compute_fake_coord(GtkDisplayPanel *, gint *, gint *);

/* Transcrit les coordonnées absolues en coordonnées à l'écran. */
void gtk_display_panel_compute_real_coord(GtkDisplayPanel *, gint *, gint *);

/* Transcrit les coordonnées absolues en coordonnées à l'écran. */
void gtk_display_panel_compute_relative_coords(GtkDisplayPanel *, gint *, gint *);



#endif  /* _GTK_DISPLAYPANEL_INT_H */
