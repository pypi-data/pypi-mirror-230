
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkbufferdisplay.c - affichage de tampons de lignes
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


#include "gtkbufferdisplay.h"


#include <assert.h>


#include "easygtk.h"
#include "gtkbufferdisplay-int.h"
#include "../core/params.h"
#include "../glibext/gbinarycursor.h" // REMME



/* -------------------------- INTERACTION DIRECTE AVEC GTK -------------------------- */


/* Procède à l'initialisation de l'afficheur de tampons. */
static void gtk_buffer_display_class_init(GtkBufferDisplayClass *);

/* Procède à l'initialisation de l'afficheur de tampons. */
static void gtk_buffer_display_init(GtkBufferDisplay *);

/* Supprime toutes les références externes. */
static void gtk_buffer_display_dispose(GtkBufferDisplay *);

/* Procède à la libération totale de la mémoire. */
static void gtk_buffer_display_finalize(GtkBufferDisplay *);

/* Intègre le focus dans le rendu du composant. */
static gboolean gtk_buffer_display_focus(GtkWidget *, GdkEventFocus *);

/* Assure la gestion des clics de souris sur le composant. */
static gboolean gtk_buffer_display_button_press(GtkWidget *, GdkEventButton *);

/* Met à jour l'affichage de la visualisation de code buffer. */
static gboolean gtk_buffer_display_draw(GtkWidget *, cairo_t *);

/* Prend en compte une frappe de touche sur le composant. */
static gboolean gtk_buffer_display_key_press(GtkWidget *, GdkEventKey *);

/* Indique les dimensions de travail du composant d'affichage. */
static void gtk_buffer_display_compute_requested_size(GtkBufferDisplay *, gint *, gint *);

/* Détermine la taille des bonds lors de défilements. */
static void gtk_buffer_display_compute_scroll_inc(GtkBufferDisplay *, gint, GtkOrientation, gdouble *, gdouble *);

/* Réagit à un défilement chez une barre associée au composant. */
static void gtk_buffer_display_adjust_scroll_value(GtkBufferDisplay *, GtkAdjustment *, GtkOrientation);

/* Indique la position d'affichage d'un emplacement donné. */
static bool gtk_buffer_display_get_cursor_coordinates(const GtkBufferDisplay *, const GLineCursor *, gint *, gint *, ScrollPositionTweak);

/* Fournit l'élément actif lié à la position courante. */
GObject *gtk_buffer_display_get_active_object(const GtkBufferDisplay *);

/* Place en cache un rendu destiné à l'aperçu graphique rapide. */
static void gtk_buffer_display_cache_glance(GtkBufferDisplay *, cairo_t *, const GtkAllocation *, double);

/* Fournit le position courante dans un panneau de chargement. */
static GLineCursor *gtk_buffer_display_get_cursor(const GtkBufferDisplay *);



/* ------------------------------ ANIMATION DU CURSEUR ------------------------------ */


/* Déplace le curseur à un emplacement défini. */
static bool _gtk_buffer_display_move_caret_to(GtkBufferDisplay *, gint, gint);

/* Déplace le curseur en effaçant son éventuelle position. */
static void gtk_buffer_display_relocate_caret(GtkBufferDisplay *, const cairo_rectangle_int_t *, GLineCursor *);

/* Assure le clignotement du curseur à l'emplacement courant. */
static gboolean gtk_buffer_display_refresh_caret(GtkBufferDisplay *);

/* Redémarre l'affichage du curseur à l'emplacement courant. */
static void gtk_buffer_display_restart_caret_blinking(GtkBufferDisplay *);

/* Prépare l'actualisation de tout ou une partie de l'affichage. */
static void gtk_buffer_display_queue_draw_caret(GtkBufferDisplay *, cairo_rectangle_int_t *);

/* Affiche le curseur à l'écran, s'il doit l'être. */
static void gtk_buffer_display_draw_caret(GtkBufferDisplay *, cairo_t *);



/* ------------------------- INCLUSION D'UNE BARRE D'OUTILS ------------------------- */


/* Place correctement la barre d'outils pour bloc. */
static void gtk_buffer_display_move_block_bar(GtkBufferDisplay *);

/* Accompagne le début du survol d'un élément de barre d'outils. */
static gboolean on_block_bar_enter_notify(GtkWidget *, GdkEventCrossing *, GtkBufferDisplay *);

/* Accompagne la fin du survol d'un élément de barre d'outils. */
static gboolean on_block_bar_leave_notify(GtkWidget *, GdkEventCrossing *, GtkBufferDisplay *);

/* Accompagne le début du survol du bouton de compression. */
static gboolean on_block_bar_collapsing_enter(GtkWidget *, GdkEventCrossing *, GtkBufferDisplay *);

/* Accompagne la fin du survol du bouton de compression. */
static gboolean on_block_bar_collapsing_leave(GtkWidget *, GdkEventCrossing *, GtkBufferDisplay *);



/* ---------------------------------------------------------------------------------- */
/*                            INTERACTION DIRECTE AVEC GTK                            */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du composant d'affichage de tampon de lignes. */
G_DEFINE_TYPE(GtkBufferDisplay, gtk_buffer_display, GTK_TYPE_DISPLAY_PANEL)


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur de tampons.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_class_init(GtkBufferDisplayClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GtkWidgetClass *widget_class;           /* Classe version Widget       */
    GtkDisplayPanelClass *panel_class;      /* Classe parente              */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_buffer_display_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_buffer_display_finalize;

    widget_class = GTK_WIDGET_CLASS(class);

    widget_class->focus_in_event = gtk_buffer_display_focus;
    widget_class->focus_out_event = gtk_buffer_display_focus;
    widget_class->button_press_event = gtk_buffer_display_button_press;
    widget_class->draw = gtk_buffer_display_draw;
    widget_class->key_press_event = gtk_buffer_display_key_press;

    panel_class = GTK_DISPLAY_PANEL_CLASS(class);

    panel_class->compute_size = (compute_requested_size_fc)gtk_buffer_display_compute_requested_size;
    panel_class->compute_inc = (compute_scroll_inc_fc)gtk_buffer_display_compute_scroll_inc;
    panel_class->adjust = (adjust_scroll_value_fc)gtk_buffer_display_adjust_scroll_value;
    panel_class->get_coordinates = (get_coordinates_fc)gtk_buffer_display_get_cursor_coordinates;
    panel_class->get_active = (get_active_object_fc)gtk_buffer_display_get_active_object;
    panel_class->move_caret_to = (move_caret_to_fc)_gtk_buffer_display_move_caret_to;
    panel_class->cache_glance = (cache_glance_fc)gtk_buffer_display_cache_glance;

    panel_class->get_cursor = (get_cursor_fc)gtk_buffer_display_get_cursor;

    /* Signaux */

    g_signal_new("reach-limit",
                 GTK_TYPE_BUFFER_DISPLAY,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkBufferDisplayClass, reach_limit),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__ENUM,
                 G_TYPE_NONE, 1, GTK_TYPE_SCROLL_TYPE);

    g_signal_new("prepare-collapsing",
                 GTK_TYPE_BUFFER_DISPLAY,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkBufferDisplayClass, prepare_collapsing),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__BOOLEAN,
                 G_TYPE_NONE, 1, G_TYPE_BOOLEAN);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à initialiser.                       *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur de tampons.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_init(GtkBufferDisplay *display)
{
    display->cursor = NULL;

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

static void gtk_buffer_display_dispose(GtkBufferDisplay *display)
{
    if (display->caret_timer != 0)
    {
        g_source_remove(display->caret_timer);
        display->caret_timer = 0;
    }

    g_clear_object(&display->view);

    g_clear_object(&display->cursor);

    g_clear_object(&display->builder);
    g_clear_object(&display->bar);

    G_OBJECT_CLASS(gtk_buffer_display_parent_class)->dispose(G_OBJECT(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = instance d'objet Gtk à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_finalize(GtkBufferDisplay *display)
{
    G_OBJECT_CLASS(gtk_buffer_display_parent_class)->finalize(G_OBJECT(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                                                                             *
*  Description : Intègre le focus dans le rendu du composant.                 *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_buffer_display_focus(GtkWidget *widget, GdkEventFocus *event)
{
    GtkBufferDisplay *display;              /* Autre version du composant  */
    gboolean has_focus;                     /* Etat courant                */

    display = GTK_BUFFER_DISPLAY(widget);
    has_focus = event->in;

    if (has_focus)
        gtk_buffer_display_restart_caret_blinking(display);

    else if (display->caret_timer != 0)
    {
        g_source_remove(display->caret_timer);
        display->caret_timer = 0;

        display->show_caret = true;
        gtk_buffer_display_queue_draw_caret(display, NULL);

    }

    return TRUE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                                                                             *
*  Description : Assure la gestion des clics de souris sur le composant.      *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_buffer_display_button_press(GtkWidget *widget, GdkEventButton *event)
{
    GtkBufferDisplay *display;              /* Autre version du composant  */
    GBufferCache *cache;                    /* Contenu représenté          */
    gint left_margin;                       /* Limite entre zones réactives*/
    gint real_x;                            /* Abscisse absolue réelle     */
    gint real_y;                            /* Ordonnée absolue réelle     */

    display = GTK_BUFFER_DISPLAY(widget);

    real_x = event->x;
    real_y = event->y;
    gtk_display_panel_compute_real_coord(GTK_DISPLAY_PANEL(display), &real_x, &real_y);

    cache = g_buffer_view_get_cache(display->view);

    left_margin = g_buffer_cache_get_left_margin(cache);

    g_object_unref(G_OBJECT(cache));

    if (real_x < left_margin)
    {
        /* TODO */
    }
    else
        _gtk_buffer_display_move_caret_to(display, real_x, real_y);

    gtk_widget_grab_focus(widget);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à redessiner.                         *
*                cr     = contexte graphique associé à l'événement.           *
*                                                                             *
*  Description : Met à jour l'affichage de la visualisation de code buffer.   *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_buffer_display_draw(GtkWidget *widget, cairo_t *cr)
{
    GtkBufferDisplay *display;              /* Autre version du composant  */
    GtkDisplayPanel *parent;                /* Autre version du composant  */
    GdkWindow *window;                      /* Fenêtre à redessiner        */
    GtkAllocation allocation;               /* Aire complète du composant  */
    cairo_region_t *region;                 /* Région visible à redessiner */
    cairo_rectangle_int_t area;             /* Surface correspondante      */
    GtkStyleContext *context;               /* Contexte du thème actuel    */
    gint virt_x;                            /* Abscisse virtuelle          */
    gint virt_y;                            /* Ordonnée virtuelle          */
    GBufferCache *cache;                    /* Contenu représenté          */
    gint left_margin;                       /* Marge gauche + espace       */
    bool sel_line;                          /* Souslignage de la sélection */
    gint *selected;                         /* Ordonnée d'une sélection    */

    display = GTK_BUFFER_DISPLAY(widget);
    parent = GTK_DISPLAY_PANEL(widget);

    window = gtk_widget_get_window(widget);

    cairo_save(cr);

    gtk_cairo_transform_to_window(cr, widget, window);

    if (parent->export)
    {
        gtk_widget_get_allocation(widget, &allocation);

        area.x = 0;
        area.y = 0;
        area.width = allocation.width;
        area.height = allocation.height;

    }
    else
    {
        region = gdk_window_get_clip_region(window);
        cairo_region_get_extents(region, &area);
        cairo_region_destroy(region);
    }

    context = gtk_widget_get_style_context(widget);

    if (parent->show_border)
    {
        gtk_widget_get_allocation(widget, &allocation);

        allocation.x = 0;
        allocation.y = 0;

        gtk_display_panel_define_border_path(parent, cr, &allocation);
        cairo_clip(cr);

    }

    /* Décalage pour le défilement horizontal */

    virt_x = 0;
    virt_y = 0;
    gtk_display_panel_compute_fake_coord(parent, &virt_x, &virt_y);

    cairo_save(cr);

    cairo_translate(cr, virt_x, 0);

    /* Récupération de la limite utile */

    cache = g_buffer_view_get_cache(display->view);

    left_margin = g_buffer_cache_get_left_margin(cache) * parent->scale;

    g_object_unref(G_OBJECT(cache));

    /* Dessin de la marge gauche */

    gtk_style_context_save(context);

    gtk_style_context_add_class(context, GTK_STYLE_CLASS_SIDEBAR);

    gtk_render_background(context, cr, 0, area.y, left_margin, area.height);

    gtk_style_context_restore(context);

    /* Fond de la zone de texte */

    gtk_style_context_save(context);

    gtk_style_context_add_class(context, GTK_STYLE_CLASS_VIEW);

    gtk_style_context_add_class(context, "graph-block-background");

    gtk_render_background(context, cr, left_margin, area.y, area.width, area.height);

    gtk_style_context_restore(context);

    if (parent->show_border)
    {
        gtk_style_context_save(context);

        gtk_style_context_add_class(context, "graph-block");

        gtk_render_background(context, cr, left_margin, area.y, area.width, area.height);

        gtk_style_context_restore(context);

    }

    /* Ligne de séparation */

    gtk_style_context_save(context);

    gtk_style_context_add_class(context, GTK_STYLE_CLASS_FRAME);

    gtk_render_frame(context, cr, - 0.5, area.y - 1, left_margin + 0.5, area.height + 2);

    gtk_style_context_restore(context);

    /* Eventuelle bordure globale */

    if (parent->show_border)
        gtk_display_panel_draw_border(parent, cr);

    /* Impression du désassemblage */

    cairo_save(cr);

    cairo_scale(cr, parent->scale, parent->scale);

    if (display->view != NULL)
    {
        g_generic_config_get_value(get_main_configuration(), MPK_SELECTION_LINE, &sel_line);
        sel_line &= gtk_widget_has_focus(widget);

        if (!sel_line || display->cursor == NULL || !g_line_cursor_is_valid(display->cursor) || parent->export)
            selected = NULL;
        else
        {
            selected = (gint []) { display->caret.y };
            gtk_display_panel_compute_relative_coords(parent, NULL, selected);
        }

        area.x -= virt_x;
        virt_y += area.y;

        g_buffer_view_draw(display->view, cr, virt_y, &area, parent->options,
                           selected, parent->scale, parent->export);

    }

    cairo_restore(cr);

    /* Curseur clignotant ? */

    cairo_restore(cr);

    if (gtk_widget_is_focus(widget))
        gtk_buffer_display_draw_caret(display, cr);

    cairo_restore(cr);

    /* Dessin des composants contenus */

    cairo_save(cr);

    cairo_scale(cr, parent->scale, parent->scale);

    GTK_WIDGET_CLASS(gtk_buffer_display_parent_class)->draw(widget, cr);

    cairo_restore(cr);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant visé par l'opération.                     *
*                event  = informations liées à l'événement.                   *
*                                                                             *
*  Description : Prend en compte une frappe de touche sur le composant.       *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_buffer_display_key_press(GtkWidget *widget, GdkEventKey *event)
{
    gboolean result;                        /* Suites à renvoyer           */
    GdkScrollDirection dir;                 /* Direction du déplacement    */
    GtkBufferDisplay *display;              /* Autre version du composant  */
    GtkDisplayPanel *panel;                 /* Autre version du composant  */
    bool ctrl;                              /* Statut de la touche Contrôle*/
    cairo_rectangle_int_t area;             /* Emplacement de curseur #1   */
    GLineCursor *cursor;                    /* Emplacement de curseur #2   */
    bool status;                            /* Validité d'un déplacement   */

    switch (event->keyval)
    {
        case GDK_KEY_Left:
            dir = GDK_SCROLL_LEFT;
            result = TRUE;
            break;

        case GDK_KEY_Up:
            dir = GDK_SCROLL_UP;
            result = TRUE;
            break;

        case GDK_KEY_Right:
            dir = GDK_SCROLL_RIGHT;
            result = TRUE;
            break;

        case GDK_KEY_Down:
            dir = GDK_SCROLL_DOWN;
            result = TRUE;
            break;

        default:
            result = FALSE;
            break;

    }

    if (result)
    {
        display = GTK_BUFFER_DISPLAY(widget);
        panel = GTK_DISPLAY_PANEL(widget);

        ctrl = (event->state & GDK_CONTROL_MASK);
        area = display->caret;

        status = g_buffer_view_move_caret(display->view, ctrl, dir, panel->options, &area, &cursor);

        if (status)
        {
            gtk_buffer_display_relocate_caret(display, &area, cursor);
            g_loaded_panel_scroll_to_cursor(G_LOADED_PANEL(panel), cursor, SPT_RAW, false);
        }
        else
            g_signal_emit_by_name(display, "reach-limit", dir);

    }

    return result;

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

static void gtk_buffer_display_compute_requested_size(GtkBufferDisplay *display, gint *width, gint *height)
{
    gint extra;                             /* Eventuel supplément largeur */

    if (width != NULL)
    {
        if (display->view != NULL)
        {
            *width = g_buffer_view_get_width(display->view, GTK_DISPLAY_PANEL(display)->options);

            if (display->bar != NULL)
            {
                gtk_widget_get_preferred_width(display->bar, NULL, &extra);
                *width += extra;
            }

        }

        else
            *width = 0;
    }

    if (height != NULL)
    {
        if (display->view != NULL)
            *height = g_buffer_view_get_height(display->view);
        else
            *height = 0;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display     = composant GTK d'affichage à consulter.         *
*                size        = taille de l'espace dans la direction donnée.   *
*                orientation = indication sur le défilement à traiter.        *
*                step        = valeur d'un petit pas de défilement. [OUT]     *
*                page        = valeur d'un grand pas de défilement. [OUT]     *
*                                                                             *
*  Description : Détermine la taille des bonds lors de défilements.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_compute_scroll_inc(GtkBufferDisplay *display, gint size, GtkOrientation orientation, gdouble *step, gdouble *page)
{
    GBufferCache *cache;                    /* Gestionnaire de lignes      */

    if (orientation == GTK_ORIENTATION_VERTICAL && display->view != NULL)
    {
        cache = g_buffer_view_get_cache(display->view);

        *step = g_buffer_cache_get_line_height(cache);
        *page = *step * 10;

        g_object_unref(G_OBJECT(cache));

    }

    else
        GTK_DISPLAY_PANEL_CLASS(gtk_buffer_display_parent_class)->compute_inc(GTK_DISPLAY_PANEL(display),
                                                                           size, orientation, step, page);

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

static void gtk_buffer_display_adjust_scroll_value(GtkBufferDisplay *display, GtkAdjustment *adj, GtkOrientation orientation)
{
    GtkWidget *widget;                      /* Autre vision du composant   */

    widget = GTK_WIDGET(display);

    if (gtk_widget_get_realized(widget))
        gdk_window_invalidate_rect(gtk_widget_get_window(widget), NULL, FALSE);

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

static bool gtk_buffer_display_get_cursor_coordinates(const GtkBufferDisplay *display, const GLineCursor *cursor, gint *x, gint *y, ScrollPositionTweak tweak)
{
    bool result;                            /* Bilan à remonter            */
    bool need_code;                         /* Recherche plus raffinée     */
    GBufferCache *cache;                    /* Gestionnaire de lignes      */
    int height;                             /* Hauteur allouée             */

    need_code = (tweak == SPT_BOTTOM);

    cache = g_buffer_view_get_cache(display->view);

    result = g_buffer_view_get_cursor_coordinates(display->view, cursor, need_code, x, y);

    if (result)
    {
        *x += g_buffer_view_get_margin(display->view, GTK_DISPLAY_PANEL(display)->options);

        height = gtk_widget_get_allocated_height(GTK_WIDGET(display));

        switch (tweak)
        {
            case SPT_RAW:
                break;

            case SPT_TOP:
                break;

            case SPT_CENTER:
                *y -= (height / 2);
                break;

            case SPT_BOTTOM:
                *y -= height;
                *y += g_buffer_cache_get_line_height(cache);
                break;

        }

    }

    g_object_unref(G_OBJECT(cache));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                                                                             *
*  Description : Fournit l'élément actif lié à la position courante.          *
*                                                                             *
*  Retour      : Objet actif courant ou NULL si aucun.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *gtk_buffer_display_get_active_object(const GtkBufferDisplay *display)
{
    GObject *result;                        /* Trouvaille à retourner      */

    /* Si aucune position n'est définie... */
    if (display->cursor == NULL || !g_line_cursor_is_valid(display->cursor))
        result = NULL;

    else
        result = g_buffer_view_find_creator(display->view,
                                            display->caret.x, display->caret.y,
                                            GTK_DISPLAY_PANEL(display)->options);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                cairo   = assistant pour la création de rendus.              *
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

static void gtk_buffer_display_cache_glance(GtkBufferDisplay *display, cairo_t *cairo, const GtkAllocation *area, double scale)
{
    cairo_set_line_width(cairo, 1);
    cairo_set_source_rgb(cairo, 0.4, 0.4, 0.4);

    cairo_rectangle(cairo, area->x + 0.5, area->y + 0.5, area->width - 1, area->height - 1);

    cairo_stroke(cairo);

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

static GLineCursor *gtk_buffer_display_get_cursor(const GtkBufferDisplay *display)
{
    GLineCursor *result;                    /* Contenu à retourner         */

    if (display->cursor != NULL)
    {
        result = display->cursor;
        g_object_ref(G_OBJECT(result));
    }
    else
        result = g_binary_cursor_new();

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                                                                             *
*  Description : Fournit la vue associée au tampon de lignes courant.         *
*                                                                             *
*  Retour      : Vue mise en place.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferView *gtk_buffer_display_get_view(const GtkBufferDisplay *display)
{
    GBufferView *result;                    /* Instance à retourner        */

    result = display->view;

    g_object_ref(G_OBJECT(result));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                                ANIMATION DU CURSEUR                                */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à consulter.                         *
*                cursor  = définition générique d'une localisation à l'écran. *
*                                                                             *
*  Description : Détermine si une position est comprise dans l'affichage.     *
*                                                                             *
*  Retour      : true si le composant comprend bien la localisation fournie.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_buffer_display_contain_cursor(const GtkBufferDisplay *display, const GLineCursor *cursor)
{
    bool result;                            /* Bilan à retourner           */
    GLineCursor *start;                     /* Position initiale du tampon */
    GLineCursor *end;                       /* Position finale du tampon   */
    int status;                             /* Bilan d'une comparaison     */

    g_buffer_view_get_restrictions(display->view, &start, &end);

    if (start == NULL && end == NULL)
        result = NULL;

    else
    {
        status = g_line_cursor_compare(start, cursor);

        if (status > 0)
            result = false;

        else
        {
            status = g_line_cursor_compare(cursor, end);

            result = (status < 0);

        }

        g_object_unref(G_OBJECT(start));
        g_object_unref(G_OBJECT(end));

    }

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

static bool _gtk_buffer_display_move_caret_to(GtkBufferDisplay *display, gint x, gint y)
{
    bool result;                            /* Bilan à retourner           */
    GtkDisplayPanel *panel;                 /* Autre version du composant  */
    cairo_rectangle_int_t new;              /* Nouvel emplacement calculé  */
    GLineCursor *cursor;                    /* Emplacement de curseur      */

    panel = GTK_DISPLAY_PANEL(display);

    result = g_buffer_view_compute_caret_full(display->view, x, y, panel->options, &new, &cursor);

    if (result)
        gtk_buffer_display_relocate_caret(display, &new, cursor);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display   = composant GTK à manipuler.                       *
*                beginning = précise le coin où se retrouvera le curseur.     *
*                same_x    = tente de conserver une même abscisse ou NULL ?   *
*                                                                             *
*  Description : Déplace le curseur à un emplacement en extrémité.            *
*                                                                             *
*  Retour      : true si un traitement a été effectué, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_buffer_display_move_caret_to(GtkBufferDisplay *display, bool beginning, gint *same_x)
{
    bool result;                            /* Bilan à remonter            */
    GBufferCache *cache;                    /* Contenu représenté          */
    gint left_margin;                       /* Limite entre zones réactives*/
    gint x;                                 /* Abscisse d'emplacement      */
    gint y;                                 /* Ordonnée d'emplacement      */

    if (beginning)
    {
        cache = g_buffer_view_get_cache(display->view);

        left_margin = g_buffer_cache_get_left_margin(cache);

        g_object_unref(G_OBJECT(cache));

        x = same_x != NULL ? *same_x : left_margin * 2;
        y = 0;

    }
    else
    {
        if (same_x != NULL)
            x = *same_x;
        else
            gtk_widget_get_preferred_width(GTK_WIDGET(display), NULL, &x);

        gtk_widget_get_preferred_height(GTK_WIDGET(display), NULL, &y);
        y--;

    }

    result = _gtk_buffer_display_move_caret_to(display, x, y);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                area    = emplacement pour le dessin d'un curseur.           *
*                cursor  = emplacement représenté dans un tampon interne.     *
*                                                                             *
*  Description : Déplace le curseur en effaçant son éventuelle position.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_relocate_caret(GtkBufferDisplay *display, const cairo_rectangle_int_t *area, GLineCursor *cursor)
{
    bool clear_old;                         /* Effacement chirurgical      */
    cairo_rectangle_int_t old_area;         /* Mémorisation de l'ancien    */
    bool need_redraw;                       /* Besoin de rafraîchissement ?*/

    if (display->cursor != NULL && g_line_cursor_is_valid(display->cursor))
    {
        clear_old = true;
        old_area = display->caret;
    }
    else
        clear_old = false;

    if (display->cursor != NULL)
        g_object_unref(G_OBJECT(display->cursor));

    display->caret = *area;
    display->cursor = cursor;

    if (GTK_BUFFER_DISPLAY_GET_CLASS(display)->notify_caret != NULL)
        need_redraw = GTK_BUFFER_DISPLAY_GET_CLASS(display)->notify_caret(display, area);
    else
        need_redraw = false;

    if (display->cursor != NULL && g_line_cursor_is_valid(display->cursor))
        gtk_buffer_display_restart_caret_blinking(display);

    if (need_redraw)
        gtk_buffer_display_queue_draw_caret(display, NULL);

    else if (clear_old)
        gtk_buffer_display_queue_draw_caret(display, &old_area);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                                                                             *
*  Description : Assure le clignotement du curseur à l'emplacement courant.   *
*                                                                             *
*  Retour      : TRUE pour poursuivre le clignotement.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_buffer_display_refresh_caret(GtkBufferDisplay *display)
{
    /* Bascule l'affichage */
    display->show_caret = !display->show_caret;

    assert(display->cursor != NULL && g_line_cursor_is_valid(display->cursor));

    if (!display->show_caret)
        gtk_buffer_display_queue_draw_caret(display, &display->caret);
    else
        gtk_buffer_display_queue_draw_caret(display, NULL);

    return TRUE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                                                                             *
*  Description : Redémarre l'affichage du curseur à l'emplacement courant.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_restart_caret_blinking(GtkBufferDisplay *display)
{

    GtkSettings *settings;                  /* Propriétés du système       */
    guint interval;                         /* Fréquence d'actualisation   */

    if (display->caret_timer != 0)
    {
        g_source_remove(display->caret_timer);
        display->caret_timer = 0;
    }

    if (display->cursor != NULL && g_line_cursor_is_valid(display->cursor))
    {
        settings = gtk_settings_get_default();

        g_object_get(settings, "gtk-cursor-blink-time", &interval, NULL);

        display->show_caret = true;

        g_object_ref(G_OBJECT(display));

        display->caret_timer = gdk_threads_add_timeout_full(G_PRIORITY_DEFAULT, interval,
                                                            (GSourceFunc)gtk_buffer_display_refresh_caret,
                                                            display, g_object_unref);

    }

    if (display->cursor != NULL)
        g_signal_emit_by_name(display, "cursor-moved", display->cursor);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                area    = emplacement du curseur ou NULL toute la région.    *
*                                                                             *
*  Description : Prépare l'actualisation de tout ou une partie de l'affichage.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_queue_draw_caret(GtkBufferDisplay *display, cairo_rectangle_int_t *area)
{
    GtkWidget *widget;                      /* Autre version du composant  */
    cairo_rectangle_int_t rect;             /* Zone rectangulaire relative */
    cairo_region_t *region;                 /* Zone précise à redessiner   */

    widget = GTK_WIDGET(display);

    if (area == NULL)
        gtk_widget_queue_draw(widget);

    else
    {
        rect = *area;
        gtk_display_panel_compute_relative_coords(GTK_DISPLAY_PANEL(display), &rect.x, &rect.y);

        region = cairo_region_create_rectangle(&rect);
        gtk_widget_queue_draw_region(widget, region);
        cairo_region_destroy(region);

    }

    /**
     * Pour une raison non comprise, le redessin n'est pris en compte que
     * si le parent est concerné également...
     */

    widget = gtk_widget_get_parent(widget);

    if (GTK_IS_SCROLLED_WINDOW(widget))
        gtk_widget_queue_draw(widget);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                cr     = contexte graphique disponible pour l'opération.     *
*                                                                             *
*  Description : Affiche le curseur à l'écran, s'il doit l'être.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_draw_caret(GtkBufferDisplay *display, cairo_t *cr)
{
    cairo_rectangle_int_t area;             /* Zone adaptée à traiter      */
    cairo_region_t *region;                 /* Région définie associée     */
    GtkWidget *widget;                      /* Autre version du composant  */
    GdkRGBA *color;                         /* Couleur du curseur          */

    if (display->cursor != NULL && g_line_cursor_is_valid(display->cursor) && display->show_caret)
    {
        area = display->caret;
        gtk_display_panel_compute_relative_coords(GTK_DISPLAY_PANEL(display), &area.x, &area.y);

        region = cairo_region_create_rectangle(&area);

        widget = GTK_WIDGET(display);

        gtk_style_context_get(gtk_widget_get_style_context(widget),
                              gtk_widget_get_state_flags(widget),
                              GTK_STYLE_PROPERTY_COLOR, &color, NULL);

        cairo_set_source_rgb(cr, color->red, color->green, color->blue);

        cairo_rectangle(cr, area.x, area.y, area.width, area.height);
        cairo_fill(cr);

        cairo_region_destroy(region);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                           INCLUSION D'UNE BARRE D'OUTILS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : display = panneau d'affichage concerné.                      *
*                                                                             *
*  Description : Ajoute une nouvelle barre d'outils pour bloc au composant.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_buffer_display_add_block_bar(GtkBufferDisplay *display)
{
    GtkWidget *bar;                         /* Barre d'outils à intégrer   */

    assert(display->builder == NULL);

    display->builder = gtk_builder_new_from_resource("/org/chrysalide/gtkext/blockbar.ui");

    bar = GTK_WIDGET(gtk_builder_get_object(display->builder, "blockbar"));

    display->bar = bar;
    g_object_ref(G_OBJECT(bar));

    g_object_ref(G_OBJECT(bar));
    gtk_widget_unparent(bar);

    gtk_fixed_put(GTK_FIXED(display), bar, 0, 0);

    gtk_builder_add_callback_symbols(display->builder,
                                     BUILDER_CALLBACK(on_block_bar_enter_notify),
                                     BUILDER_CALLBACK(on_block_bar_leave_notify),
                                     BUILDER_CALLBACK(on_block_bar_collapsing_enter),
                                     BUILDER_CALLBACK(on_block_bar_collapsing_leave),
                                     NULL);

    gtk_builder_connect_signals(display->builder, display);

    gtk_buffer_display_move_block_bar(display);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = panneau d'affichage concerné.                      *
*                                                                             *
*  Description : Place correctement la barre d'outils pour bloc.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_buffer_display_move_block_bar(GtkBufferDisplay *display)
{
    GtkWidget *bar;                         /* Barre d'outils courante     */
    gint width;                             /* Largeur requise à vide      */

    bar = display->bar;
    display->bar = NULL;

    gtk_buffer_display_compute_requested_size(display, &width, NULL);

    display->bar = bar;

    gtk_fixed_move(GTK_FIXED(display), bar, width, (int)BORDER_CORNER_RADIUS / 2);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique concerné par l'opération.      *
*                event   = informations liées à l'événement.                  *
*                display = panneau d'affichage impliqué par l'action.         *
*                                                                             *
*  Description : Accompagne le début du survol d'un élément de barre d'outils.*
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_block_bar_enter_notify(GtkWidget *widget, GdkEventCrossing *event, GtkBufferDisplay *display)
{
    gtk_widget_set_opacity(widget, 1.0);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique concerné par l'opération.      *
*                event   = informations liées à l'événement.                  *
*                display = panneau d'affichage impliqué par l'action.         *
*                                                                             *
*  Description : Accompagne la fin du survol d'un élément de barre d'outils.  *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_block_bar_leave_notify(GtkWidget *widget, GdkEventCrossing *event, GtkBufferDisplay *display)
{
    gtk_widget_set_opacity(widget, 0.6);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique concerné par l'opération.      *
*                event   = informations liées à l'événement.                  *
*                display = panneau d'affichage impliqué par l'action.         *
*                                                                             *
*  Description : Accompagne le début du survol du bouton de compression.      *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_block_bar_collapsing_enter(GtkWidget *widget, GdkEventCrossing *event, GtkBufferDisplay *display)
{
    g_signal_emit_by_name(display, "prepare-collapsing", FALSE);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique concerné par l'opération.      *
*                event   = informations liées à l'événement.                  *
*                display = panneau d'affichage impliqué par l'action.         *
*                                                                             *
*  Description : Accompagne la fin du survol du bouton de compression.        *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_block_bar_collapsing_leave(GtkWidget *widget, GdkEventCrossing *event, GtkBufferDisplay *display)
{
    g_signal_emit_by_name(display, "prepare-collapsing", TRUE);

    return FALSE;

}
