
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkgraphdisplay.c - affichage de morceaux de code sous forme graphique
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


#include "gtkgraphdisplay.h"


#include <assert.h>
#include <math.h>


#include <i18n.h>


#include "gtkblockdisplay.h"
#include "gtkbufferdisplay.h"
#include "gtkdisplaypanel-int.h"
#include "graph/cluster.h"
#include "../analysis/routine.h"
#include "../common/extstr.h"
#include "../format/format.h"
#include "../glibext/gbinarycursor.h"
#include "../glibext/gloadedpanel.h"
#include "../gui/core/items.h"



/* Composant d'affichage sous forme graphique (instance) */
struct _GtkGraphDisplay
{
    GtkDisplayPanel parent;                 /* A laisser en premier        */
    GtkWidget *support;                     /* Support des vues en bloc    */
    GtkWidget *extender;                    /* Force la taille du support  */

    GBinSymbol *routine;                    /* Routine en cours d'affichage*/

    segcnt_list *highlighted;               /* Segments mis en évidence    */

    GGraphCluster *cluster;                 /* Disposition en graphique    */
    GtkAllocation collapsing_area;          /* Aire à compresser           */
    bool may_collapsing;                    /* Validité de cette aire      */

    GGraphEdge **edges;                     /* Liens entre les noeuds      */
    size_t edges_count;                     /* Quantité de ces liens       */
    size_t hl_edge_index;                   /* Indice du lien survolé      */

    gdouble start_x;                        /* Abscisse du point de souris */
    gdouble start_y;                        /* Ordonnée du point de souris */
    bool big_enough;                        /* Capacités de déplacement ?  */
    gdouble ref_h;                          /* Position horizontale de ref.*/
    gdouble ref_v;                          /* Position verticale de ref.  */

};

/* Composant d'affichage sous forme graphique (classe) */
struct _GtkGraphDisplayClass
{
    GtkDisplayPanelClass parent;            /* A laisser en premier        */

};


/* Profondeur de l'ombre */
#define SHADOW_SIZE 4

/* Marges en bordure de graphique */
#define GRAPH_MARGIN 23

/* Taille du cadrillage pour l'aperçu des compressions */
#define COLLAPSING_GRID_SIZE 4


/* Initialise la classe générique des graphiques de code. */
static void gtk_graph_display_class_init(GtkGraphDisplayClass *);

/* Initialise une instance d'afficheur de code en graphique. */
static void gtk_graph_display_init(GtkGraphDisplay *);

/* Supprime toutes les références externes. */
static void gtk_graph_display_dispose(GtkGraphDisplay *);

/* Procède à la libération totale de la mémoire. */
static void gtk_graph_display_finalize(GtkGraphDisplay *);

/* S'adapte à la surface concédée par le composant parent. */
static void gtk_graph_display_size_allocate(GtkWidget *, GtkAllocation *);

/* Centre si possible le contenu du panneau d'affichage. */
static void gtk_graph_display_update_support_margins(GtkGraphDisplay *, const GtkAllocation *);

/* Indique les dimensions de travail du composant d'affichage. */
static void gtk_graph_display_compute_requested_size(GtkGraphDisplay *, gint *, gint *);

/* Réagit à un défilement chez une barre associée au composant. */
static void gtk_graph_display_adjust_scroll_value(GtkGraphDisplay *, GtkAdjustment *, GtkOrientation);

/*  Met à jour l'affichage de la vue sous forme graphique. */
static gboolean gtk_graph_display_draw(GtkWidget *, cairo_t *, GtkGraphDisplay *);

/* Assure la gestion des clics de souris sur le composant. */
static gboolean gtk_graph_display_button_press(GtkWidget *, GdkEventButton *, GtkGraphDisplay *);

/* Assure la gestion des clics de souris sur le composant. */
static gboolean gtk_graph_display_button_release(GtkWidget *, GdkEventButton *, GtkGraphDisplay *);

/* Assure la suivi des déplacements de souris sur le composant. */
static gboolean gtk_graph_display_motion_notify(GtkWidget *, GdkEventMotion *, GtkGraphDisplay *);

/* Réagit à une fin de survol du support graphique. */
static gboolean gtk_graph_display_on_leave_notify(GtkWidget *, GdkEventCrossing *, GtkGraphDisplay *);

/* Prépare l'affichage d'une astuce. */
static gboolean gtk_graph_display_query_tooltip(GtkWidget *, gint, gint, gboolean, GtkTooltip *, GtkGraphDisplay *);

/* Ajuste au besoin la zone affichée pour un curseur. */
static void gtk_graph_display_prepare_for_cursor(GtkGraphDisplay *, const GLineCursor *);

/* Indique la position d'affichage d'un emplacement donné. */
static bool gtk_graph_display_get_cursor_coordinates(const GtkGraphDisplay *, const GLineCursor *, gint *, gint *, ScrollPositionTweak);

/* Déplace le curseur à un emplacement défini. */
static bool gtk_graph_display_move_caret_to(GtkGraphDisplay *, gint, gint);

/* Fournit le position courante dans un panneau de chargement. */
static GLineCursor *gtk_graph_display_get_cursor(const GtkGraphDisplay *);

/* Place en cache un rendu destiné à l'aperçu graphique rapide. */
static void gtk_graph_display_cache_glance(GtkGraphDisplay *, cairo_t *, const GtkAllocation *, double);

/* Spécifie l'échelle à appliquer à l'affichage du composant. */
static void gtk_graph_display_apply_scale(GtkGraphDisplay *, double, double);

/* Marque ou non le composant pour une exportation prochaine. */
static void gtk_graph_display_prepare_export(GtkGraphDisplay *, bool);

/* Supprime tout contenu de l'afficheur de code en graphique. */
static void gtk_graph_display_reset(GtkGraphDisplay *, bool);

/* Notifie un changement de surbrillance au sein d'un noeud. */
static void gtk_graph_display_changed_highlights(GtkBlockDisplay *, GtkGraphDisplay *);

/* Notifie une incapacité de déplacement au sein d'un noeud. */
static void gtk_graph_display_reach_caret_limit(GtkBufferDisplay *, GdkScrollDirection, GtkGraphDisplay *);

/* Prend note de la proximité d'une compression de blocs. */
static void gtk_graph_display_prepare_collasping(GtkBufferDisplay *, gboolean, GtkGraphDisplay *);



/* Détermine le type du composant d'affichage en graphique. */
G_DEFINE_TYPE(GtkGraphDisplay, gtk_graph_display, GTK_TYPE_DISPLAY_PANEL)


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Initialise la classe générique des graphiques de code.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_class_init(GtkGraphDisplayClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GtkWidgetClass *widget_class;           /* Classe de haut niveau       */
    GtkDisplayPanelClass *panel_class;      /* Classe parente              */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_graph_display_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_graph_display_finalize;

    widget_class = GTK_WIDGET_CLASS(class);

    widget_class->size_allocate = gtk_graph_display_size_allocate;

    panel_class = GTK_DISPLAY_PANEL_CLASS(class);

    panel_class->compute_size = (compute_requested_size_fc)gtk_graph_display_compute_requested_size;
    panel_class->adjust = (adjust_scroll_value_fc)gtk_graph_display_adjust_scroll_value;
    panel_class->prepare = (prepare_for_cursor_fc)gtk_graph_display_prepare_for_cursor;

    panel_class->get_coordinates = (get_coordinates_fc)gtk_graph_display_get_cursor_coordinates;
    panel_class->move_caret_to = (move_caret_to_fc)gtk_graph_display_move_caret_to;
    panel_class->get_cursor = (get_cursor_fc)gtk_graph_display_get_cursor;
    panel_class->cache_glance = (cache_glance_fc)gtk_graph_display_cache_glance;

    panel_class->scale = (apply_scale_fc)gtk_graph_display_apply_scale;

    panel_class->prepare_export = (prepare_export_fc)gtk_graph_display_prepare_export;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = instance GTK à initialiser.                        *
*                                                                             *
*  Description : Initialise une instance d'afficheur de code en graphique.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_init(GtkGraphDisplay *display)
{
    display->support = gtk_fixed_new();
    gtk_widget_set_has_window(display->support, TRUE);
    gtk_widget_set_can_focus(display->support, TRUE);

    g_signal_connect(G_OBJECT(display->support), "draw",
                     G_CALLBACK(gtk_graph_display_draw), display);

    g_signal_connect(G_OBJECT(display->support), "button-press-event",
                     G_CALLBACK(gtk_graph_display_button_press), display);
    g_signal_connect(G_OBJECT(display->support), "button-release-event",
                     G_CALLBACK(gtk_graph_display_button_release), display);
    g_signal_connect(G_OBJECT(display->support), "motion-notify-event",
                     G_CALLBACK(gtk_graph_display_motion_notify), display);
    g_signal_connect(G_OBJECT(display->support), "leave-notify-event",
                     G_CALLBACK(gtk_graph_display_on_leave_notify), display);
    g_signal_connect(G_OBJECT(display->support), "query-tooltip",
                     G_CALLBACK(gtk_graph_display_query_tooltip), display);

    g_object_set(G_OBJECT(display->support), "has-tooltip", TRUE, NULL);

    gtk_widget_add_events(display->support,
                          GDK_BUTTON_MOTION_MASK | GDK_BUTTON_PRESS_MASK | GDK_BUTTON_RELEASE_MASK
                          | GDK_LEAVE_NOTIFY_MASK | GDK_POINTER_MOTION_MASK);

    gtk_widget_show(display->support);

    gtk_fixed_put(GTK_FIXED(display), display->support, 0, 0);

    display->extender = gtk_fixed_new();

    gtk_widget_set_margin_end(display->extender, 1);
    gtk_widget_set_margin_top(display->extender, 1);

    gtk_widget_show(display->extender);
    gtk_fixed_put(GTK_FIXED(display->support), display->extender, 0, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_dispose(GtkGraphDisplay *display)
{
    /**
     * display->support est traité par la version amont du conteneur, propriétaire
     * du composant GTK.
     *
     * Pareil pour display->extender.
     */

    gtk_graph_display_reset(display, true);

    G_OBJECT_CLASS(gtk_graph_display_parent_class)->dispose(G_OBJECT(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_finalize(GtkGraphDisplay *display)
{
    G_OBJECT_CLASS(gtk_graph_display_parent_class)->finalize(G_OBJECT(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget     = composant GTK à mettre à jour.                  *
*                allocation = étendue accordée à la vue.                      *
*                                                                             *
*  Description : S'adapte à la surface concédée par le composant parent.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_size_allocate(GtkWidget *widget, GtkAllocation *allocation)
{
    GtkGraphDisplay *display;                     /* Autre version du composant  */

    GTK_WIDGET_CLASS(gtk_graph_display_parent_class)->size_allocate(widget, allocation);

    display = GTK_GRAPH_DISPLAY(widget);

    gtk_graph_display_update_support_margins(display, allocation);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display    = panneau dont le contenu est à déplacer.         *
*                allocation = étendue accordée à la vue.                      *
*                                                                             *
*  Description : Centre si possible le contenu du panneau d'affichage.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_update_support_margins(GtkGraphDisplay *display, const GtkAllocation *allocation)
{
    gint width;                             /* Largeur totale du support   */
    gint height;                            /* Hauteur totale du support   */
    gint start;                             /* Bordure horizontale         */
    gint top;                               /* Bordure verticale           */

    gtk_graph_display_compute_requested_size(display, &width, &height);

    if (width > allocation->width)
        start = 0;
    else
        start = (allocation->width - width) / 2;

    if (height > allocation->height)
        top = 0;
    else
        top = (allocation->height - height) / 2;

    gtk_widget_set_margin_start(display->support, start);
    gtk_widget_set_margin_top(display->support, top);

    gtk_widget_queue_resize(GTK_WIDGET(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                width   = largeur requise à renseigner ou NULL. [OUT]        *
*                height  = hauteur requise à renseigner ou NULL. [OUT]        *
*                                                                             *
*  Description : Indique les dimensions de travail du composant d'affichage.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_compute_requested_size(GtkGraphDisplay *display, gint *width, gint *height)
{
    GtkAllocation needed;                   /* Taille requise              */

    if (display->cluster != NULL)
    {
        g_graph_cluster_compute_needed_alloc(display->cluster, &needed);

        /**
         * Les liens latéraux peuvent décaler les composants du graphique vers
         * la droite, donc needed.x est parfois non nul.
         *
         * Il n'y a ainsi pas d'assurance d'obtenir needed.x == 0, et on ajuste
         * en fonction de ce décalage.
         */

        assert(needed.y == 0);

        needed.width += needed.x;

        needed.width += 2 * GRAPH_MARGIN;
        needed.height += 2 * GRAPH_MARGIN;

    }
    else
    {
        needed.width = 0;
        needed.height = 0;
    }

    if (width != NULL) *width = needed.width;
    if (height != NULL) *height = needed.height;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display     = panneau d'affichage concerné.                  *
*                adj         = défilement dont une valeur a changé.           *
*                orientation = indication sur le défilement à traiter.        *
*                                                                             *
*  Description : Réagit à un défilement chez une barre associée au composant. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_adjust_scroll_value(GtkGraphDisplay *display, GtkAdjustment *adj, GtkOrientation orientation)
{
    gint fake_x;                            /* Abscisse virtuelle          */
    gint fake_y;                            /* Ordonnée virtuelle          */

    fake_x = 0;
    fake_y = 0;
    gtk_display_panel_compute_fake_coord(GTK_DISPLAY_PANEL(display), &fake_x, &fake_y);

    gtk_fixed_move(GTK_FIXED(display), display->support, fake_x, -fake_y);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK à redessiner.                        *
*                cr      = contexte graphique associé à l'événement.          *
*                display = support maître à consulter.                        *
*                                                                             *
*  Description : Met à jour l'affichage de la vue sous forme graphique.       *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_graph_display_draw(GtkWidget *widget, cairo_t *cr, GtkGraphDisplay *display)
{
    GtkDisplayPanel *parent;                /* Autre version du composant  */
    cairo_surface_t *pat_image;             /* Fond du futur pinceau       */
    cairo_t *pat_cr;                        /* Pinceau pour le pinceau     */
    cairo_pattern_t *pattern;               /* Patron de remplissage       */
    double degrees;                         /* Conversion en degrés        */
    size_t i;                               /* Boucle de parcours          */

    parent = GTK_DISPLAY_PANEL(display);

    /* Eventuel fond pour la zone de compression */

    if (display->may_collapsing && !GTK_DISPLAY_PANEL(display)->export)
    {
        cairo_save(cr);

        cairo_scale(cr, parent->scale, parent->scale);

        /* Préparation du pinceau */

        pat_image = cairo_image_surface_create(CAIRO_FORMAT_ARGB32,
                                               2 * COLLAPSING_GRID_SIZE, 2 * COLLAPSING_GRID_SIZE);

        pat_cr = cairo_create(pat_image);

        cairo_set_source_rgba(pat_cr, 1.0, 1.0, 1.0, 0.05);

        cairo_rectangle(pat_cr,
                        0, 0,
                        COLLAPSING_GRID_SIZE, COLLAPSING_GRID_SIZE);

        cairo_fill(pat_cr);

        cairo_rectangle(pat_cr,
                        COLLAPSING_GRID_SIZE, COLLAPSING_GRID_SIZE,
                        COLLAPSING_GRID_SIZE, COLLAPSING_GRID_SIZE);

        cairo_fill(pat_cr);

        pattern = cairo_pattern_create_for_surface(pat_image);
        cairo_pattern_set_extend(pattern, CAIRO_EXTEND_REPEAT);


        /* Dessin de la zone */

        degrees = M_PI / 180.0;

        cairo_arc(cr,
                  display->collapsing_area.x + BORDER_CORNER_RADIUS,
                  display->collapsing_area.y + BORDER_CORNER_RADIUS,
                  BORDER_CORNER_RADIUS, 180 * degrees, 270 * degrees);

        cairo_line_to(cr,
                      display->collapsing_area.x + display->collapsing_area.width - BORDER_CORNER_RADIUS,
                      display->collapsing_area.y);

        cairo_arc(cr,
                  display->collapsing_area.x + display->collapsing_area.width - BORDER_CORNER_RADIUS,
                  display->collapsing_area.y + BORDER_CORNER_RADIUS,
                  BORDER_CORNER_RADIUS, 270 * degrees, 360 * degrees);

        cairo_line_to(cr,
                      display->collapsing_area.x + display->collapsing_area.width,
                      display->collapsing_area.y + display->collapsing_area.height - BORDER_CORNER_RADIUS);

        cairo_arc(cr,
                  display->collapsing_area.x + display->collapsing_area.width - BORDER_CORNER_RADIUS,
                  display->collapsing_area.y + display->collapsing_area.height - BORDER_CORNER_RADIUS,
                  BORDER_CORNER_RADIUS, 0 * degrees, 90 * degrees);

        cairo_line_to(cr,
                      display->collapsing_area.x + BORDER_CORNER_RADIUS,
                      display->collapsing_area.y + display->collapsing_area.height);

        cairo_arc(cr,
                  display->collapsing_area.x + BORDER_CORNER_RADIUS,
                  display->collapsing_area.y + display->collapsing_area.height - BORDER_CORNER_RADIUS,
                  BORDER_CORNER_RADIUS, 90 * degrees, 180 * degrees);

        cairo_close_path(cr);

        cairo_set_source(cr, pattern);

        cairo_fill(cr);

        /* Sortie propre */

        cairo_pattern_destroy(pattern);

        cairo_destroy(pat_cr);

        cairo_surface_destroy(pat_image);

        cairo_restore(cr);

    }

    /* Dessin des ombres */

    cairo_save(cr);

    cairo_scale(cr, parent->scale, parent->scale);

    void draw_shadow(GtkWidget *child, gpointer unused)
    {
        GGraphCluster *cluster;             /* Cluster correspondant       */
        GtkAllocation alloc;                /* Emplacement de l'enfant     */
        GtkAllocation area;                 /* Emplacement à considérer    */
        gint j;                             /* Boucle de parcours          */
        cairo_pattern_t *pattern;           /* Zones d'application         */

        /* On évite l'extenseur de support... */
        if (!GTK_IS_DISPLAY_PANEL(child))
            return;

        cluster = g_graph_cluster_find_by_widget(display->cluster, child);
        assert(cluster != NULL);

        g_graph_cluster_get_allocation(cluster, &alloc);

        alloc.x += GRAPH_MARGIN;
        alloc.y += GRAPH_MARGIN;

        area = alloc;

        for (j = 1; j < SHADOW_SIZE; j++)
        {
            cairo_push_group(cr);

            area.x = alloc.x + j;
            area.y = alloc.y + j;

            gtk_display_panel_define_border_path(GTK_DISPLAY_PANEL(child), cr, &area);
            cairo_set_source_rgba(cr, 0.0, 0.0, 0.0, 1.0);
            cairo_fill(cr);

            cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE);

            gtk_display_panel_define_border_path(GTK_DISPLAY_PANEL(child), cr, &alloc);
            cairo_set_source_rgba(cr, 0.0, 0.0, 0.0, 0.0);
            cairo_fill(cr);

            pattern = cairo_pop_group(cr);

            cairo_set_source_rgba(cr, 0.0, 0.0, 0.0, 0.3);
            cairo_mask(cr, pattern);
            cairo_fill(cr);

            cairo_pattern_destroy(pattern);

        }

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)draw_shadow, NULL);

    for (i = 0; i < display->edges_count; i++)
        g_graph_edge_draw(display->edges[i], cr, true, display->hl_edge_index == i);

    cairo_restore(cr);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK visé par l'opération.                *
*                event   = informations liées à l'événement.                  *
*                display = support maître à consulter.                        *
*                                                                             *
*  Description : Assure la gestion des clics de souris sur le composant.      *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_graph_display_button_press(GtkWidget *widget, GdkEventButton *event, GtkGraphDisplay *display)
{
    gboolean result;                        /* Poursuite à faire suivre    */
    GtkScrolledWindow *support;             /* Support défilant associé    */
    GtkAdjustment *hadj;                    /* Gestionnaire du défilement  */
    GtkAdjustment *vadj;                    /* Gestionnaire du défilement  */
    GdkCursor *cursor;                      /* Pointeur pour la surface    */

    result = FALSE;

    if (event->button == 1)
    {
        support = GTK_SCROLLED_WINDOW(gtk_widget_get_parent(GTK_WIDGET(display)));

        hadj = gtk_scrolled_window_get_hadjustment(support);
        vadj = gtk_scrolled_window_get_vadjustment(support);

        display->big_enough = (gtk_adjustment_get_upper(hadj) > gtk_adjustment_get_page_size(hadj)
                            || gtk_adjustment_get_upper(vadj) > gtk_adjustment_get_page_size(vadj));

        if (display->big_enough)
        {
            display->start_x = event->x_root;
            display->start_y = event->y_root;

            display->ref_h = gtk_adjustment_get_value(hadj);
            display->ref_v = gtk_adjustment_get_value(vadj);

            cursor = gdk_cursor_new_for_display(gdk_display_get_default(), GDK_FLEUR);
            gdk_window_set_cursor(gtk_widget_get_window(widget), cursor);
            g_object_unref(G_OBJECT(cursor));

            result = TRUE;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK visé par l'opération.                *
*                event   = informations liées à l'événement.                  *
*                display = support maître à consulter.                        *
*                                                                             *
*  Description : Assure la gestion des clics de souris sur le composant.      *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_graph_display_button_release(GtkWidget *widget, GdkEventButton *event, GtkGraphDisplay *display)
{
    if (event->button == 1 && display->big_enough)
        gdk_window_set_cursor(gtk_widget_get_window(widget), NULL);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK visé par l'opération.                *
*                event   = informations liées à l'événement.                  *
*                display = support maître à consulter.                        *
*                                                                             *
*  Description : Assure la suivi des déplacements de souris sur le composant. *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_graph_display_motion_notify(GtkWidget *widget, GdkEventMotion *event, GtkGraphDisplay *display)
{
    gdouble diff_x;                         /* Evolution sur les abscisses */
    gdouble diff_y;                         /* Evolution sur les ordonnées */
    GtkScrolledWindow *support;             /* Support défilant associé    */
    GtkAdjustment *hadj;                    /* Gestionnaire du défilement  */
    GtkAdjustment *vadj;                    /* Gestionnaire du défilement  */
    gdouble value;                          /* Nouvelle valeur bornée      */
    double scale;                           /* Echelle appliquée au rendu  */
    size_t i;                               /* Boucle de parcours          */

    /* Déplacement du graphique ? */
    if (event->state & GDK_BUTTON1_MASK)
    {
        if (!display->big_enough)
            goto done;

        diff_x = display->start_x - event->x_root;
        diff_y = display->start_y - event->y_root;

        support = GTK_SCROLLED_WINDOW(gtk_widget_get_parent(GTK_WIDGET(display)));

        hadj = gtk_scrolled_window_get_hadjustment(support);
        vadj = gtk_scrolled_window_get_vadjustment(support);

        value = CLAMP(display->ref_h + diff_x, gtk_adjustment_get_lower(hadj),
                      gtk_adjustment_get_upper(hadj) - gtk_adjustment_get_page_size(hadj));
        gtk_adjustment_set_value(hadj, value);

        value = CLAMP(display->ref_v + diff_y, gtk_adjustment_get_lower(vadj),
                      gtk_adjustment_get_upper(vadj) - gtk_adjustment_get_page_size(vadj));
        gtk_adjustment_set_value(vadj, value);

    }

    /* Survol d'un lien ? */
    else
    {
        scale = GTK_DISPLAY_PANEL(display)->scale;

        for (i = 0; i < display->edges_count; i++)
            if (g_graph_edge_detect_at(display->edges[i], event->x / scale, event->y / scale))
            {
                display->hl_edge_index = i;
                break;
            }

        if (i < display->edges_count)
            gtk_widget_queue_draw(widget);

        else if (display->hl_edge_index < display->edges_count)
        {
            display->hl_edge_index = display->edges_count;
            gtk_widget_queue_draw(widget);
        }

    }

 done:

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK visé par l'opération.                *
*                event   = informations liées à l'événement.                  *
*                display = support maître à consulter.                        *
*                                                                             *
*  Description : Réagit à une fin de survol du support graphique.             *
*                                                                             *
*  Retour      : TRUE pour arrêter la propagation du signal, FALSE sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_graph_display_on_leave_notify(GtkWidget *widget, GdkEventCrossing *event, GtkGraphDisplay *display)
{
    if (display->hl_edge_index < display->edges_count)
    {
        display->hl_edge_index = display->edges_count;
        gtk_widget_queue_draw(widget);
    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget   = composant GTK visé par l'opération.               *
*                x        = abscisse de la position du message.               *
*                y        = ordonnée de la position du message.               *
*                keyboard = indique une demande suite à obtiention du focus.  *
*                tooltip  = astuce à compléter. [OUT]                         *
*                display  = support maître à consulter.                       *
*                                                                             *
*  Description : Prépare l'affichage d'une astuce.                            *
*                                                                             *
*  Retour      : TRUE pour un affichage validé, FALSE sinon.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_graph_display_query_tooltip(GtkWidget *widget, gint x, gint y, gboolean keyboard, GtkTooltip *tooltip, GtkGraphDisplay *display)
{
    gboolean result;                        /* Bilan à retourner           */
    GCodeBlock *src;                        /* Bloc d'origine du lien      */
    GCodeBlock *dst;                        /* Bloc de destination du lien */
    char *info;                             /* Information à faire paraître*/
    char *desc;                             /* Description d'un bloc       */

    result = FALSE;

    if (display->hl_edge_index < display->edges_count)
    {
        g_graph_edge_get_boundaries(display->edges[display->hl_edge_index], &src, &dst);

        info = stradd(NULL, _("<b>Source:</b> "));

        desc = g_code_block_build_tooltip(src);
        info = stradd(info, desc);
        free(desc);

        info = stradd(info, "\n\n");

        info = stradd(info, _("<b>Destination:</b> "));

        desc = g_code_block_build_tooltip(dst);
        info = stradd(info, desc);
        free(desc);

        gtk_tooltip_set_markup(tooltip, info);
        free(info);

        g_object_unref(G_OBJECT(src));
        g_object_unref(G_OBJECT(dst));

        result = TRUE;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à mettre à jour.                     *
*                cursor  = emplacement à présenter à l'écran.                 *
*                                                                             *
*  Description : Ajuste au besoin la zone affichée pour un curseur.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_prepare_for_cursor(GtkGraphDisplay *display, const GLineCursor *cursor)
{
    vmpa2t addr;                            /* Adresse ciblée              */
    bool need_update;                       /* Mise à jour du contenu ?    */
    const mrange_t *range;                  /* Couverture courante         */
    GExeFormat *format;                     /* Type de fichier chargé      */
    GBinSymbol *symbol;                     /* Symbole présent à l'adresse */
    bool found;                             /* Bilan des recherches        */
    SymbolType type;                        /* Type de symbole rencontré   */
    GBlockList *list;                       /* Liste de blocs basiques     */
    gint right;                             /* Abscisse du coin droit      */
    gint bottom;                            /* Ordonnée du coin inférieur  */
    GtkAllocation allocation;               /* Espace alloué au panneau    */
    GtkWidget *child;                       /* Composant sélectionné       */

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    if (display->routine == NULL)
        need_update = true;
    else
    {
        range = g_binary_symbol_get_range(display->routine);
        need_update = !mrange_contains_addr(range, &addr);
    }

    if (need_update)
    {
        gtk_graph_display_reset(display, false);

        if (!g_line_cursor_is_valid(cursor))
            goto no_valid_cursor;

        format = g_loaded_binary_get_format(GTK_DISPLAY_PANEL(display)->binary);

        found = g_binary_format_find_symbol_for(G_BIN_FORMAT(format), &addr, &symbol);

        if (!found)
            goto no_symbol_found;

        type = g_binary_symbol_get_stype(symbol);

        if (type != STP_ROUTINE && type != STP_ENTRY_POINT)
            goto bad_symbol_type;

        display->routine = symbol;
        g_object_ref(G_OBJECT(symbol));

        display->highlighted = init_segment_content_list();

        list = g_binary_routine_get_basic_blocks(G_BIN_ROUTINE(symbol));

        display->cluster = bootstrap_graph_cluster(GTK_DISPLAY_PANEL(display)->binary,
                                                   list, display->highlighted);

        g_object_unref(G_OBJECT(list));

        g_graph_cluster_place(display->cluster, display);

        /**
         * Comme la taille du support ne peut pas être forcée et
         * étendue pour comprendre les ombres, on place un composant
         * minuscule à l'extrémité de ce support.
         */

        gtk_graph_display_compute_requested_size(display, &right, &bottom);

        gtk_fixed_move(GTK_FIXED(display->support), display->extender, right - 1, bottom - 1);

        /**
         * Si possible, on centre le contenu obtenu.
         */

        gtk_widget_get_allocation(GTK_WIDGET(display), &allocation);

        gtk_graph_display_update_support_margins(display, &allocation);

        gtk_widget_size_allocate(GTK_WIDGET(display), &allocation);

        /**
         * Première sélection...
         */

        child = g_graph_cluster_get_widget(display->cluster);

        gtk_container_set_focus_child(GTK_CONTAINER(display->support), child);

        g_object_unref(G_OBJECT(child));

 bad_symbol_type:

        g_object_unref(G_OBJECT(symbol));

 no_symbol_found:

        update_editor_items_current_view(G_LOADED_PANEL(display));

        g_object_unref(G_OBJECT(format));

 no_valid_cursor:

        ;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                cursor  = emplacement à présenter à l'écran.                 *
*                x       = position horizontale au sein du composant. [OUT]   *
*                y       = position verticale au sein du composant. [OUT]     *
*                tweak   = adaptation finale à effectuer.                     *
*                                                                             *
*  Description : Indique la position d'affichage d'un emplacement donné.      *
*                                                                             *
*  Retour      : true si l'adresse fait partie du composant, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool gtk_graph_display_get_cursor_coordinates(const GtkGraphDisplay *display, const GLineCursor *cursor, gint *x, gint *y, ScrollPositionTweak tweak)
{
    bool result;                            /* Bilan final à retourner     */
    GList *children;                        /* Sous-composants à parcourir */
    GList *iter;                            /* Boucle de parcours          */
    GtkWidget *child;                       /* Composant embarqué          */
    GtkAllocation alloc;                    /* Emplacement réservé         */

    result = false;

    children  = gtk_container_get_children(GTK_CONTAINER(display->support));

    for (iter = g_list_first(children); iter != NULL; iter = g_list_next(iter))
    {
        child = GTK_WIDGET(iter->data);

        if (!GTK_IS_BUFFER_DISPLAY(child))
            continue;

        result = gtk_buffer_display_contain_cursor(GTK_BUFFER_DISPLAY(child), cursor);

        if (result)
        {
            result = gtk_display_panel_get_cursor_coordinates(GTK_DISPLAY_PANEL(child), cursor, x, y, tweak);
            assert(result);

            gtk_widget_get_allocation(child, &alloc);

            *x += alloc.x;
            *y += alloc.y;
            break;
        }

    }

    g_list_free(children);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                x       = abscisse proposée pour le nouvel emplacement.      *
*                y       = ordonnée proposée pour le nouvel emplacement.      *
*                                                                             *
*  Description : Déplace le curseur à un emplacement défini.                  *
*                                                                             *
*  Retour      : true si un traitement a été effectué, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool gtk_graph_display_move_caret_to(GtkGraphDisplay *display, gint x, gint y)
{
    bool result;                            /* Bilan à retourner           */

    result = false;

    void move_caret_to_sub_block(GtkWidget *child, gpointer unused)
    {
        GtkAllocation alloc;                /* Emplacement réservé         */
        GtkDisplayPanel *panel;             /* Autre vision d'enfance      */
        gint sub_x;                         /* Abscisse relative à l'enfant*/
        gint sub_y;                         /* Ordonnée relative à l'enfant*/

        if (result)
            return;

        if (!GTK_IS_BUFFER_DISPLAY(child))
            return;

        gtk_widget_get_allocation(child, &alloc);

        if (x < alloc.x || x >= (alloc.x + alloc.width)) return;
        if (y < alloc.y || y >= (alloc.y + alloc.height)) return;

        panel = GTK_DISPLAY_PANEL(child);

        sub_x = x - alloc.x;
        sub_y = y - alloc.y;

        result = GTK_DISPLAY_PANEL_GET_CLASS(panel)->move_caret_to(panel, sub_x, sub_y);

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)move_caret_to_sub_block, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                                                                             *
*  Description : Fournit le position courante dans un panneau de chargement.  *
*                                                                             *
*  Retour      : Informations relatives à la position du curseur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GLineCursor *gtk_graph_display_get_cursor(const GtkGraphDisplay *display)
{
    GLineCursor *result;                    /* Contenu à retourner         */
    GtkWidget *child;                       /* Composant sélectionné       */

    child = gtk_container_get_focus_child(GTK_CONTAINER(display->support));

    if (child != NULL)
        result = g_loaded_panel_get_cursor(G_LOADED_PANEL(child));
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                cr      = assistant pour la création de rendus.              *
*                area    = taille de la surface réduite à disposition.        *
*                scale   = échelle vis à vis de la taille réelle.             *
*                                                                             *
*  Description : Place en cache un rendu destiné à l'aperçu graphique rapide. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_cache_glance(GtkGraphDisplay *display, cairo_t *cr, const GtkAllocation *area, double scale)
{
    GtkDisplayPanel *parent;                /* Autre version du composant  */
    size_t i;                               /* Boucle de parcours          */

    parent = GTK_DISPLAY_PANEL(display);

    cairo_scale(cr, scale * parent->scale, scale * parent->scale);

    void draw_child_glance(GtkWidget *child, gpointer unused)
    {
        GGraphCluster *cluster;             /* Cluster correspondant       */
        GtkAllocation sub_area;             /* Emplacement réservé         */

        if (!GTK_IS_BUFFER_DISPLAY(child))
            return;

        cluster = g_graph_cluster_find_by_widget(display->cluster, child);
        assert(cluster != NULL);

        g_graph_cluster_get_allocation(cluster, &sub_area);

        sub_area.x += GRAPH_MARGIN;
        sub_area.y += GRAPH_MARGIN;

        g_loaded_panel_cache_glance(G_LOADED_PANEL(child), cr, &sub_area, scale);

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)draw_child_glance, NULL);

    for (i = 0; i < display->edges_count; i++)
        g_graph_edge_draw(display->edges[i], cr, false, false);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à mettre à jour.                     *
*                old     = ancienne échelle appliquée.                        *
*                new     = nouvelle échelle à appliquer.                      *
*                                                                             *
*  Description : Spécifie l'échelle à appliquer à l'affichage du composant.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_apply_scale(GtkGraphDisplay *display, double old, double new)
{
    GtkDisplayPanel *parent;                /* Autre version du composant  */
    gint right;                             /* Abscisse du coin droit      */
    gint bottom;                            /* Ordonnée du coin inférieur  */

    /* Traitement des blocs */

    void apply_child_scale(GtkWidget *child, gpointer unused)
    {
        GGraphCluster *cluster;             /* Cluster correspondant       */
        GtkAllocation sub_area;             /* Emplacement réservé         */
        gint x;                             /* Abscisse du point d'arrivée */
        gint y;                             /* Ordonnée du point d'arrivée */

        if (!GTK_IS_BUFFER_DISPLAY(child))
            return;

        cluster = g_graph_cluster_find_by_widget(display->cluster, child);
        assert(cluster != NULL);

        g_graph_cluster_get_allocation(cluster, &sub_area);

        x = (GRAPH_MARGIN + sub_area.x) * new;
        y = (GRAPH_MARGIN + sub_area.y) * new;

        gtk_fixed_move(GTK_FIXED(display->support), child, x, y);

        gtk_display_panel_set_scale(GTK_DISPLAY_PANEL(child), new);

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)apply_child_scale, NULL);

    /* Calcul du nouvel espace nécessaire */

    parent = GTK_DISPLAY_PANEL(display);

    gtk_graph_display_compute_requested_size(display, &right, &bottom);

    right *= parent->scale;
    bottom *= parent->scale;

    gtk_fixed_move(GTK_FIXED(display->support), display->extender, right - 1, bottom - 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à mettre à jour.                     *
*                export  = préparation d'une exportation complète du rendu ?  *
*                                                                             *
*  Description : Marque ou non le composant pour une exportation prochaine.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_prepare_export(GtkGraphDisplay *display, bool export)
{
    void prepare_child_export(GtkWidget *child, gpointer unused)
    {
        if (!GTK_IS_BUFFER_DISPLAY(child))
            return;

        gtk_display_panel_prepare_export(GTK_DISPLAY_PANEL(child), export);

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)prepare_child_export, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau composant pour l'affichage en graphique.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_graph_display_new(void)
{
    return g_object_new(GTK_TYPE_GRAPH_DISPLAY, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                                                                             *
*  Description : Fournit le support utilisé pour le rendu graphique.          *
*                                                                             *
*  Retour      : Composant GTK de support.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_graph_display_get_support(GtkGraphDisplay *display)
{
    GtkWidget *result;                      /* Instance à retourner        */

    result = display->support;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à mettre à jour.                     *
*                widget  = composant GTK à insérer.                           *
*                alloc   = position du point d'insertion.                     *
*                                                                             *
*  Description : Place une vue sous forme de bloc dans le graphique.          *
*                                                                             *
*  Retour      : Plutôt que de redéfinir *toutes* les méthodes de             *
*                GtkContainer, on étend !                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_graph_display_put(GtkGraphDisplay *display, GtkWidget *widget, const GtkAllocation *alloc)
{
    g_signal_connect(widget, "reach-limit", G_CALLBACK(gtk_graph_display_reach_caret_limit), display);
    g_signal_connect(widget, "prepare-collapsing", G_CALLBACK(gtk_graph_display_prepare_collasping), display);
    g_signal_connect(widget, "highlight-changed", G_CALLBACK(gtk_graph_display_changed_highlights), display);

    gtk_fixed_put(GTK_FIXED(display->support), widget, GRAPH_MARGIN + alloc->x, GRAPH_MARGIN + alloc->y);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à mettre à jour.                     *
*                edge    = lien entre noeuds à conserver.                     *
*                                                                             *
*  Description : Intègre un lien entre blocs graphiques dans l'afficheur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_graph_display_add_edge(GtkGraphDisplay *display, GGraphEdge *edge)
{
    g_graph_edge_offset(edge, GRAPH_MARGIN, GRAPH_MARGIN);

    display->edges = realloc(display->edges, ++display->edges_count * sizeof(GGraphEdge *));

    display->edges[display->edges_count - 1] = edge;

    display->hl_edge_index = display->edges_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = instance GTK à réinitialiser.                      *
*                dispose = indique l'origine de l'appel.                      *
*                                                                             *
*  Description : Supprime tout contenu de l'afficheur de code en graphique.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_reset(GtkGraphDisplay *display, bool dispose)
{
    size_t i;                               /* Boucle de parcours          */

    if (!dispose)
    {
        void detach_all_blocks(GtkWidget *widget, GtkContainer *container)
        {
            if (widget != display->extender)
                gtk_container_remove(container, widget);

        }

        gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)detach_all_blocks, display->support);

    }

    if (display->routine != NULL)
    {
        g_object_unref(G_OBJECT(display->routine));
        display->routine = NULL;
    }

    if (display->highlighted != NULL)
    {
        unref_segment_content_list(display->highlighted);
        display->highlighted = NULL;
    }

    if (display->cluster != NULL)
    {
        g_object_unref(G_OBJECT(display->cluster));
        display->cluster = NULL;
    }

    display->may_collapsing = false;

    for (i = 0; i < display->edges_count; i++)
        g_object_unref(G_OBJECT(display->edges[i]));

    if (display->edges_count > 0)
    {
        free(display->edges);
        display->edges = NULL;

        display->edges_count = 0;
        display->hl_edge_index = 0;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = composant d'affichage impliqué dans la procédure.  *
*                display = support graphique de tous les noeuds.              *
*                                                                             *
*  Description : Notifie un changement de surbrillance au sein d'un noeud.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_changed_highlights(GtkBlockDisplay *node, GtkGraphDisplay *display)
{
    void refresh_highlights(GtkWidget *child, gpointer unused)
    {
        if (!GTK_IS_BUFFER_DISPLAY(child))
            return;

        if (child != GTK_WIDGET(node))
            gtk_widget_queue_draw(child);

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)refresh_highlights, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = composant d'affichage impliqué dans la procédure.  *
*                dir     = direction du déplacement souhaité et impossible.   *
*                display = support graphique de tous les noeuds.              *
*                                                                             *
*  Description : Notifie une incapacité de déplacement au sein d'un noeud.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_reach_caret_limit(GtkBufferDisplay *node, GdkScrollDirection dir, GtkGraphDisplay *display)
{
#if 0
    GBufferView *view;                      /* Vue d'un tampon global      */
    vmpa2t first;                           /* Début d'un groupe de lignes */
    vmpa2t last;                            /* Fin d'un groupe de lignes   */
    const mrange_t *range;                  /* Couverture courante         */
    GArchProcessor *proc;                   /* Processeur pour instructions*/
    vmpa2t iaddr;                           /* Position de l'instructin    */
    instr_iter_t *iter;                     /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction à venir visiter */
#ifndef NDEBUG
    bool is_return;                         /* Est-ce une instruc. finale ?*/
#endif
    GtkBufferDisplay *target;               /* Bloc suivant pour le focus  */

    /* Détermination de l'instruction à cibler */

    view = gtk_buffer_display_get_view(node);
    g_buffer_view_get_restrictions(view, &first, &last);
    g_object_unref(G_OBJECT(view));

    range = g_binary_symbol_get_range(display->routine);

    proc = g_loaded_binary_get_processor(GTK_DISPLAY_PANEL(display)->binary);

    init_vmpa(&iaddr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

#ifndef NDEBUG
    is_return = false;
#endif

    switch (dir)
    {
        case GDK_SCROLL_LEFT:
        case GDK_SCROLL_UP:

            if (cmp_vmpa(get_mrange_addr(range), &first) != 0)
            {
                iter = g_arch_processor_get_iter_from_address(proc, &first);

                if (iter != NULL)
                {
                    instr = get_instruction_iterator_prev(iter);

                    if (instr != NULL)
                    {
                        /* TODO : boucler si !HAS_CODE */

                        if (mrange_contains_addr(range, &iaddr))
                            copy_vmpa(&iaddr, get_mrange_addr(g_arch_instruction_get_range(instr)));

                        g_object_unref(G_OBJECT(instr));

                    }

                    delete_instruction_iterator(iter);

                }

            }

            break;

        case GDK_SCROLL_RIGHT:
        case GDK_SCROLL_DOWN:

            iter = g_arch_processor_get_iter_from_address(proc, &last);

            if (iter != NULL)
            {
#ifndef NDEBUG
                instr = get_instruction_iterator_current(iter);
                if (instr != NULL)
                {
                    is_return = (g_arch_instruction_get_flags(instr) & AIF_RETURN_POINT);
                    g_object_unref(G_OBJECT(instr));
                }
#endif

                instr = get_instruction_iterator_next(iter);

                if (instr != NULL)
                {
                    /* TODO : boucler si !HAS_CODE */

                    copy_vmpa(&iaddr, get_mrange_addr(g_arch_instruction_get_range(instr)));

                    if (!mrange_contains_addr(range, &iaddr))
                        init_vmpa(&iaddr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

                    g_object_unref(G_OBJECT(instr));

                }

                delete_instruction_iterator(iter);

            }

            break;

        case GDK_SCROLL_SMOOTH:
            assert(false);  /* Argument jamais généré */
            break;

    }

    g_object_unref(G_OBJECT(proc));

    /* Recherche du bloc parent */

    if (is_invalid_vmpa(&iaddr))
        return;

    target = NULL;

    void find_target_block(GtkWidget *child, gpointer unused)
    {
        GtkBufferDisplay *test;             /* Candidat potentiel à tester */

        if (!GTK_IS_BUFFER_DISPLAY(child))
            return;

        test = GTK_BUFFER_DISPLAY(child);

        view = gtk_buffer_display_get_view(test);
        g_buffer_view_get_restrictions(view, &first, &last);
        g_object_unref(G_OBJECT(view));

        if (cmp_vmpa(&first, &iaddr) <= 0 && cmp_vmpa(&iaddr, &last) <= 0)
        {
            assert(target == NULL);
            assert(node != test);
            target = test;
            return;
        }

    }

    gtk_container_foreach(GTK_CONTAINER(display->support), (GtkCallback)find_target_block, NULL);

    assert(target != NULL || is_return);

    /* Affichage du nouveau curseur */

    /**
     * Il se peut qu'aucune adresse suivante ne soit disponible : c'est typiquement
     * le cas sous ARM, avec les valeurs brutes référencées dans le code. Ces valeurs
     * sont incluses dans la surface couverte par la routine concernée, mais ne sont
     * pas intégrées dans les blocs basiques associés.
     */

    if (target == NULL)
        return;

    gtk_widget_grab_focus(GTK_WIDGET(target));

    switch (dir)
    {
        case GDK_SCROLL_UP:
        case GDK_SCROLL_LEFT:
            gtk_buffer_display_move_caret_to(target, false, NULL);
            break;

            break;

        case GDK_SCROLL_RIGHT:
        case GDK_SCROLL_DOWN:
            gtk_buffer_display_move_caret_to(target, true, NULL);
            break;

            break;

        case GDK_SCROLL_SMOOTH:
            assert(false);  /* Argument jamais généré */
            break;

    }

    /* TODO : scrolling... */
#endif
}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = composant d'affichage impliqué dans la procédure.  *
*                done    = indique si la préparation est à jeter.             *
*                display = support graphique de tous les noeuds.              *
*                                                                             *
*  Description : Prend note de la proximité d'une compression de blocs.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_graph_display_prepare_collasping(GtkBufferDisplay *node, gboolean done, GtkGraphDisplay *display)
{
    GGraphCluster *cluster;                 /* Ensemble à priori concerné  */

    if (!done)
    {
        cluster = g_graph_cluster_find_by_widget(display->cluster, GTK_WIDGET(node));

        if (cluster == NULL)
            done = TRUE;

        else
        {
            g_graph_cluster_compute_needed_alloc(cluster, &display->collapsing_area);
            g_object_unref(G_OBJECT(cluster));

            display->collapsing_area.x += GRAPH_MARGIN;
            display->collapsing_area.y += GRAPH_MARGIN;

            assert(BORDER_CORNER_RADIUS < GRAPH_MARGIN);

            display->collapsing_area.x -= BORDER_CORNER_RADIUS;
            display->collapsing_area.y -= BORDER_CORNER_RADIUS;
            display->collapsing_area.width += 2 * BORDER_CORNER_RADIUS;
            display->collapsing_area.height += 2 * BORDER_CORNER_RADIUS;

        }

    }

    display->may_collapsing = !done;

    gtk_widget_queue_draw(GTK_WIDGET(display));

}
