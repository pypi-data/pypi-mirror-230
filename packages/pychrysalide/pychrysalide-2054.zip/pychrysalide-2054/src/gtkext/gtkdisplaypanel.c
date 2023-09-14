
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdisplaypanel.c - affichage de contenus de binaire
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


#include "gtkdisplaypanel.h"


#include <math.h>


#include "gtkdisplaypanel-int.h"
#include "../glibext/chrysamarshal.h"
#include "../glibext/gbinarycursor.h"    // REMME
#include "../glibext/gloadedpanel-int.h"



/* Procède à l'initialisation de l'afficheur générique. */
static void gtk_display_panel_class_init(GtkDisplayPanelClass *);

/* Procède à l'initialisation de l'afficheur générique. */
static void gtk_display_panel_init(GtkDisplayPanel *);

/* Procède à l'initialisation de l'interface d'affichage. */
static void gtk_display_panel_loaded_interface_init(GLoadedPanelInterface *);

/* Supprime toutes les références externes. */
static void gtk_display_panel_dispose(GtkDisplayPanel *);

/* Procède à la libération totale de la mémoire. */
static void gtk_display_panel_finalize(GtkDisplayPanel *);

/* Définit une propriété du composant d'affichage. */
static void gtk_display_panel_set_property(GObject *, guint, const GValue *, GParamSpec *);

/* Fournit une propriété du composant d'affichage. */
static void gtk_display_panel_get_property(GObject *, guint, GValue *, GParamSpec *);

/* Détruit un composant d'affichage. */
static void gtk_display_panel_destroy(GtkWidget *);

/* Encadre la construction graphique initiale de l'affichage. */
static void gtk_display_panel_realize(GtkWidget *);

/* S'adapte à la surface concédée par le composant parent. */
static void gtk_display_panel_size_allocate(GtkWidget *, GtkAllocation *);

/* Fournit la hauteur idéale pour le composant d'affichage. */
static void gtk_display_panel_get_preferred_height(GtkWidget *, gint *, gint *);

/* Fournit la largeur idéale pour le composant d'affichage. */
static void gtk_display_panel_get_preferred_width(GtkWidget *, gint *, gint *);

/* Détermine la taille des bonds lors de défilements. */
static void gtk_display_panel_compute_scroll_inc(GtkDisplayPanel *, gint, GtkOrientation, gdouble *, gdouble *);

/* Détermine la taille allouée pour le contenu. */
static void gtk_display_panel_compute_allocation(GtkDisplayPanel *, GtkAllocation *);

/* Se débarrsse d'un ajustement pour un défilement donné. */
static void gtk_display_panel_disconnect_adjustment(GtkDisplayPanel *, GtkOrientation);

/* S'associe à un ajustement pour un défilement donné. */
static void gtk_display_panel_set_adjustment(GtkDisplayPanel *, GtkOrientation, GtkAdjustment *);

/* Ajuste les paramètres de défilement du composant. */
static void gtk_display_panel_update_adjustment(GtkDisplayPanel *, GtkOrientation);

/* Réagit à un défilement chez une barre associée au composant.*/
static void gtk_display_panel_adjustment_value_changed(GtkAdjustment *, GtkDisplayPanel *);



/* ----------------------- INTERFACE DE PANNEAU DE CHARGEMENT ----------------------- */


/* Réagit à un changement des règles d'affichage. */
static void on_display_panel_option_change(GDisplayOptions *, size_t, bool, GtkDisplayPanel *);

/* Associe à un panneau d'affichage un binaire chargé. */
static void gtk_display_panel_set_content(GtkDisplayPanel *, GLoadedContent *);

/* Fournit le contenu associé à un panneau de chargement. */
static GLoadedContent *gtk_display_panel_get_content(const GtkDisplayPanel *);

/* Fournit le position courante dans un panneau de chargement. */
static GLineCursor *gtk_display_panel_get_cursor(const GtkDisplayPanel *);

/* S'assure qu'un emplacement donné est visible à l'écran. */
static void gtk_display_panel_scroll_to_cursor(GtkDisplayPanel *, const GLineCursor *, ScrollPositionTweak, bool);

/* Place en cache un rendu destiné à l'aperçu graphique rapide. */
static void gtk_display_panel_cache_glance(GtkDisplayPanel *, cairo_t *, const GtkAllocation *, double);



/* Détermine le type du composant d'affichage générique. */
G_DEFINE_TYPE_WITH_CODE(GtkDisplayPanel, gtk_display_panel, GTK_TYPE_FIXED,
                        G_IMPLEMENT_INTERFACE(GTK_TYPE_SCROLLABLE, NULL)
                        G_IMPLEMENT_INTERFACE(G_TYPE_LOADED_PANEL, gtk_display_panel_loaded_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur générique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_class_init(GtkDisplayPanelClass *class)
{
    GObjectClass *object;                   /* Plus haut niveau équivalent */
    GtkWidgetClass *widget;                 /* Classe de haut niveau       */
    GtkDisplayPanelClass *panel;            /* Classe de lus bas niveau    */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_display_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_display_panel_finalize;
    object->set_property = gtk_display_panel_set_property;
    object->get_property = gtk_display_panel_get_property;

    /* Implémentation de l'interface "GtkScrollable" */
    g_object_class_override_property(object, VPP_HADJUSTMENT, "hadjustment");
    g_object_class_override_property(object, VPP_VADJUSTMENT, "vadjustment");
    g_object_class_override_property(object, VPP_HSCROLL_POLICY, "hscroll-policy");
    g_object_class_override_property(object, VPP_VSCROLL_POLICY, "vscroll-policy");

    widget = GTK_WIDGET_CLASS(class);

    widget->destroy = gtk_display_panel_destroy;
    widget->realize = gtk_display_panel_realize;
    widget->size_allocate = gtk_display_panel_size_allocate;
    widget->get_preferred_height = gtk_display_panel_get_preferred_height;
    widget->get_preferred_width = gtk_display_panel_get_preferred_width;

    panel = GTK_DISPLAY_PANEL_CLASS(class);

    panel->compute_inc = gtk_display_panel_compute_scroll_inc;

    /* Signaux */

    g_signal_new("scaled",
                 GTK_TYPE_DISPLAY_PANEL,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkDisplayPanelClass, scaled),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__DOUBLE_DOUBLE,
                 G_TYPE_NONE, 2, G_TYPE_DOUBLE, G_TYPE_DOUBLE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à initialiser.                         *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur générique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_init(GtkDisplayPanel *panel)
{
    gtk_widget_set_has_window(GTK_WIDGET(panel), TRUE);
    gtk_widget_set_can_focus(GTK_WIDGET(panel), TRUE);

    panel->scale = 1.0;

    panel->export = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface d'affichage.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_loaded_interface_init(GLoadedPanelInterface *iface)
{
    iface->set_content = (set_loaded_panel_content_fc)gtk_display_panel_set_content;
    iface->get_content = (get_loaded_panel_content_fc)gtk_display_panel_get_content;

    iface->get_cursor = (get_loaded_cursor_fc)gtk_display_panel_get_cursor;
    iface->scroll = (scroll_loaded_to_cursor_fc)gtk_display_panel_scroll_to_cursor;

    iface->cache_glance = (cache_loaded_glance_fc)gtk_display_panel_cache_glance;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_dispose(GtkDisplayPanel *panel)
{
    g_clear_object(&panel->hadjustment);
    g_clear_object(&panel->vadjustment);

    g_clear_object(&panel->options);

    g_clear_object(&panel->binary);

    G_OBJECT_CLASS(gtk_display_panel_parent_class)->dispose(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_finalize(GtkDisplayPanel *panel)
{
    G_OBJECT_CLASS(gtk_display_panel_parent_class)->finalize(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = instance de composant GTK à manipuler.             *
*                prop_id = identifiant de la propriété concernée.             *
*                value   = valeur attribuée.                                  *
*                pspec   = spécification de la propriété visée.               *
*                                                                             *
*  Description : Définit une propriété du composant d'affichage.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_set_property(GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec)
{
    GtkDisplayPanel *panel;                 /* Autre vision de l'instance  */

    panel = GTK_DISPLAY_PANEL(object);

    switch (prop_id)
    {
        case VPP_HADJUSTMENT:
            gtk_display_panel_set_adjustment(panel, GTK_ORIENTATION_HORIZONTAL, g_value_get_object(value));
            break;
        case VPP_VADJUSTMENT:
            gtk_display_panel_set_adjustment(panel, GTK_ORIENTATION_VERTICAL, g_value_get_object(value));
            break;
        case VPP_HSCROLL_POLICY:
            //viewport->priv->hscroll_policy = g_value_get_enum (value);
            //gtk_widget_queue_resize (GTK_WIDGET (viewport));
            break;
        case VPP_VSCROLL_POLICY:
            //viewport->priv->vscroll_policy = g_value_get_enum (value);
            //gtk_widget_queue_resize (GTK_WIDGET (viewport));
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
            break;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = instance de composant GTK à manipuler.             *
*                prop_id = identifiant de la propriété concernée.             *
*                value   = valeur à renvoyer.                                 *
*                pspec   = spécification de la propriété visée.               *
*                                                                             *
*  Description : Fournit une propriété du composant d'affichage.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_get_property(GObject *object, guint prop_id, GValue *value, GParamSpec *pspec)
{
    GtkDisplayPanel *panel;                 /* Autre vision de l'instance  */

    panel = GTK_DISPLAY_PANEL(object);

    switch (prop_id)
    {
        case VPP_HADJUSTMENT:
            g_value_set_object(value, panel->hadjustment);
            break;
        case VPP_VADJUSTMENT:
            g_value_set_object(value, panel->vadjustment);
            break;
        case VPP_HSCROLL_POLICY:
            g_value_set_enum(value, panel->hscroll_policy);
            break;
        case VPP_VSCROLL_POLICY:
            g_value_set_enum(value, panel->vscroll_policy);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
            break;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à détruire.                           *
*                                                                             *
*  Description : Détruit un composant d'affichage.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_destroy(GtkWidget *widget)
{
    GtkDisplayPanel *panel;                 /* Autre version du composant  */

    panel = GTK_DISPLAY_PANEL(widget);

    gtk_display_panel_disconnect_adjustment(panel, GTK_ORIENTATION_HORIZONTAL);
    gtk_display_panel_disconnect_adjustment(panel, GTK_ORIENTATION_VERTICAL);

    GTK_WIDGET_CLASS(gtk_display_panel_parent_class)->destroy(widget);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à préparer.                           *
*                                                                             *
*  Description : Encadre la construction graphique initiale de l'affichage.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_realize(GtkWidget *widget)
{
    GtkAllocation allocation;               /* Disposition du composant    */
    GdkWindowAttr attributes;               /* Propriétés du composant     */
    guint attributes_mask;                  /* Masque de prise en compte   */
    GdkWindow *window;                      /* Fenêtre du composant        */

    gtk_widget_get_allocation(widget, &allocation);

    gtk_widget_set_realized(widget, TRUE);

    attributes.window_type = GDK_WINDOW_CHILD;
    attributes.x = allocation.x;
    attributes.y = allocation.y;
    attributes.width = allocation.width;
    attributes.height = allocation.height;

    attributes.wclass = GDK_INPUT_OUTPUT;
    attributes.event_mask = gtk_widget_get_events(widget)
        | GDK_EXPOSURE_MASK
        | GDK_POINTER_MOTION_MASK | GDK_BUTTON_PRESS_MASK
        | GDK_FOCUS_CHANGE_MASK
        | GDK_SCROLL_MASK | GDK_SMOOTH_SCROLL_MASK;

    attributes_mask = GDK_WA_X | GDK_WA_Y;

    window = gdk_window_new(gtk_widget_get_parent_window(widget),
                            &attributes, attributes_mask);

    gtk_widget_set_window(widget, window);
    gtk_widget_register_window(widget, window);

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

static void gtk_display_panel_size_allocate(GtkWidget *widget, GtkAllocation *allocation)
{
    GtkDisplayPanel *panel;                 /* Autre version du composant  */

    GTK_WIDGET_CLASS(gtk_display_panel_parent_class)->size_allocate(widget, allocation);

    panel = GTK_DISPLAY_PANEL(widget);

    gtk_display_panel_update_adjustment(panel, GTK_ORIENTATION_HORIZONTAL);
    gtk_display_panel_update_adjustment(panel, GTK_ORIENTATION_VERTICAL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK à examiner.                          *
*                minimum = hauteur minimale à préciser ou NULL. [OUT]         *
*                natural = hauteur idéale à préciser ou NULL. [OUT]           *
*                                                                             *
*  Description : Fournit la hauteur idéale pour le composant d'affichage.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_get_preferred_height(GtkWidget *widget, gint *minimum, gint *natural)
{
    GtkDisplayPanel *panel;                 /* Autre version du composant  */
    gint req;                               /* Dimension requise           */

    panel = GTK_DISPLAY_PANEL(widget);

    GTK_DISPLAY_PANEL_GET_CLASS(widget)->compute_size(panel, NULL, &req);

    req *= panel->scale;

    if (minimum != NULL) *minimum = req;
    if (natural != NULL) *natural = req;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant GTK à examiner.                          *
*                minimum = largeur minimale à préciser ou NULL. [OUT]         *
*                natural = largeur idéale à préciser ou NULL. [OUT]           *
*                                                                             *
*  Description : Fournit la largeur idéale pour le composant d'affichage.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_get_preferred_width(GtkWidget *widget, gint *minimum, gint *natural)
{
    GtkDisplayPanel *panel;                 /* Autre version du composant  */
    gint req;                               /* Dimension requise           */

    panel = GTK_DISPLAY_PANEL(widget);

    GTK_DISPLAY_PANEL_GET_CLASS(widget)->compute_size(panel, &req, NULL);

    req *= panel->scale;

    if (minimum != NULL) *minimum = req;
    if (natural != NULL) *natural = req;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel       = composant GTK d'affichage à mettre à jour.     *
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

static void gtk_display_panel_compute_scroll_inc(GtkDisplayPanel *panel, gint size, GtkOrientation orientation, gdouble *step, gdouble *page)
{
    *step = size * 0.1;
    *page = size * 0.9;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                alloc = emplacement à déterminer. [OUT]                      *
*                                                                             *
*  Description : Détermine la taille allouée pour le contenu.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_compute_allocation(GtkDisplayPanel *panel, GtkAllocation *alloc)
{
    GtkWidget *widget;                      /* Autre vision du composant   */
    GtkAllocation allocation;               /* Emplacement du composant    */
    GtkStyleContext *context;               /* Contexte du style           */
    GtkStateFlags state;                    /* Etat du composant           */
    GtkBorder padding;                      /* Espace d'un espacement      */
    GtkBorder border;                       /* Espace d'une bordure        */

    widget = GTK_WIDGET(panel);

    gtk_widget_get_allocation(widget, &allocation);

    context = gtk_widget_get_style_context(widget);
    state = gtk_widget_get_state_flags(widget);

    gtk_style_context_save(context);
    gtk_style_context_add_class(context, GTK_STYLE_CLASS_FRAME);

    gtk_style_context_get_padding(context, state, &padding);
    gtk_style_context_get_border(context, state, &border);

    gtk_style_context_restore(context);

    /* Positions */

    if (panel->show_border)
    {
        alloc->x = border.left;
        alloc->y = border.top;
    }
    else
    {
        alloc->x = 0;
        alloc->y = 0;
    }

    alloc->x += padding.left;
    alloc->y += padding.top;

    /* Dimensions */

    if (panel->show_border)
    {
        alloc->width = MAX (1, allocation.width - alloc->x - padding.right - border.right);
        alloc->height = MAX (1, allocation.height - alloc->y - padding.bottom - border.bottom);
    }
    else
    {
        alloc->width = MAX (1, allocation.width - alloc->x - padding.right);
        alloc->height = MAX (1, allocation.height - alloc->y - padding.bottom);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel       = composant GTK d'affichage à mettre à jour.     *
*                orientation = indication sur le défilement à traiter.        *
*                                                                             *
*  Description : Se débarrsse d'un ajustement pour un défilement donné.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_disconnect_adjustment(GtkDisplayPanel *panel, GtkOrientation orientation)
{
    GtkAdjustment **adjp;                   /* Ajustement à manipuler      */

    adjp = orientation == GTK_ORIENTATION_HORIZONTAL ? &panel->hadjustment : &panel->vadjustment;

    if (*adjp != NULL)
    {
        g_signal_handlers_disconnect_by_func(*adjp, gtk_display_panel_adjustment_value_changed, panel);
        g_object_unref(G_OBJECT(*adjp));
        *adjp = NULL;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel       = composant GTK d'affichage à mettre à jour.     *
*                orientation = indication sur le défilement à traiter.        *
*                adj         = nouvel ajustement à prendre en compte.         *
*                                                                             *
*  Description : S'associe à un ajustement pour un défilement donné.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_set_adjustment(GtkDisplayPanel *panel, GtkOrientation orientation, GtkAdjustment *adj)
{
    GtkAdjustment **adjp;                   /* Ajustement à manipuler      */

    adjp = orientation == GTK_ORIENTATION_HORIZONTAL ? &panel->hadjustment : &panel->vadjustment;

    /* S'il n'y a rien à faire... */
    if (adj != NULL && adj == *adjp)
        return;

    if (!adj)
        adj = gtk_adjustment_new(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

    gtk_display_panel_disconnect_adjustment(panel, orientation);

    *adjp = adj;
    g_object_ref_sink(adj);

    gtk_display_panel_update_adjustment(panel, orientation);

    g_signal_connect(adj, "value-changed", G_CALLBACK(gtk_display_panel_adjustment_value_changed), panel);

    gtk_display_panel_adjustment_value_changed(adj, panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel       = composant GTK d'affichage à mettre à jour.     *
*                orientation = indication sur le défilement à traiter.        *
*                                                                             *
*  Description : Ajuste les paramètres de défilement du composant.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_update_adjustment(GtkDisplayPanel *panel, GtkOrientation orientation)
{
    GtkAllocation allocation;               /* Emplacement du contenu      */
    GtkAdjustment *adj;                     /* Ajustement à manipuler      */
    gint req;                               /* Dimension requise           */
    gint allocated;                         /* Dimension allouée           */
    gdouble step_inc;                       /* Pas de défilement           */
    gdouble page_inc;                       /* ENjambée de défilement      */

    gtk_display_panel_compute_allocation(panel, &allocation);

    if (orientation == GTK_ORIENTATION_HORIZONTAL)
    {
        adj = panel->hadjustment;

        gtk_widget_get_preferred_width(GTK_WIDGET(panel), &req, NULL);
        allocated = allocation.width;

    }
    else
    {
        adj = panel->vadjustment;

        gtk_widget_get_preferred_height(GTK_WIDGET(panel), &req, NULL);
        allocated = allocation.height;

    }

    GTK_DISPLAY_PANEL_GET_CLASS(panel)->compute_inc(panel, allocated, orientation, &step_inc, &page_inc);

    gtk_adjustment_configure(adj, gtk_adjustment_get_value(adj),
                             0, MAX(req, allocated),
                             step_inc,
                             page_inc,
                             allocated);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : adj   = défilement dont une valeur a changé.                 *
*                panel = panneau d'affichage concerné.                        *
*                                                                             *
*  Description : Réagit à un défilement chez une barre associée au composant. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_adjustment_value_changed(GtkAdjustment *adj, GtkDisplayPanel *panel)
{
    GtkOrientation orientation;             /* Indification de la barre    */

    orientation = (adj == panel->hadjustment ? GTK_ORIENTATION_HORIZONTAL : GTK_ORIENTATION_VERTICAL);

    if (GTK_DISPLAY_PANEL_GET_CLASS(panel)->adjust != NULL)
        GTK_DISPLAY_PANEL_GET_CLASS(panel)->adjust(panel, adj, orientation);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à mettre à jour.                       *
*                                                                             *
*  Description : Indique l'échelle appliquée à l'affichage du composant.      *
*                                                                             *
*  Retour      : Echelle appliquée à l'affichage.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

double gtk_display_panel_get_scale(const GtkDisplayPanel *panel)
{
    double result;                          /* Echelle à retourner         */

    result = panel->scale;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à mettre à jour.                       *
*                scale = échelle appliquée à l'affichage.                     *
*                                                                             *
*  Description : Spécifie l'échelle à appliquer à l'affichage du composant.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_set_scale(GtkDisplayPanel *panel, double scale)
{
    double old_scale;                       /* Echelle précédente          */
    GtkDisplayPanelClass *class;            /* Classe associée au composant*/

    if (scale > 1.0)
        scale = 1.0;

    else if (scale < 0.01)
        scale = 0.01;

    if (panel->scale != scale)
    {
        old_scale = panel->scale;

        panel->scale = scale;

        class = GTK_DISPLAY_PANEL_GET_CLASS(panel);

        if (class->scale != NULL)
            class->scale(panel, old_scale, scale);

        gtk_widget_queue_resize(GTK_WIDGET(panel));

        g_signal_emit_by_name(panel, "scaled", old_scale, scale);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à mettre à jour.                       *
*                show  = état de l'affichage auquel parvenir.                 *
*                                                                             *
*  Description : Définit si une bordure est à afficher.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_show_border(GtkDisplayPanel *panel, bool show)
{
    panel->show_border = show;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant GTK à mettre à jour.                      *
*                export = préparation d'une exportation complète du rendu ?   *
*                                                                             *
*  Description : Marque ou non le composant pour une exportation prochaine.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_prepare_export(GtkDisplayPanel *panel, bool export)
{
    GtkDisplayPanelClass *class;            /* Classe associée au composant*/

    panel->export = export;

    class = GTK_DISPLAY_PANEL_GET_CLASS(panel);

    if (class->prepare_export != NULL)
        class->prepare_export(panel, export);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à venir consulter.                     *
*                cr    = contexte graphique associé à l'événement.            *
*                area  = surface à considérer.                                *
*                                                                             *
*  Description : Définit un chemin décrivant la bordure autour du panneau.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_define_border_path(GtkDisplayPanel *panel, cairo_t *cr, const GtkAllocation *area)
{
    double degrees;                         /* Conversion en degrés        */

    degrees = M_PI / 180.0;

    cairo_new_sub_path(cr);

    cairo_arc(cr,
              area->x + area->width - BORDER_CORNER_RADIUS - 0.5,
              area->y + BORDER_CORNER_RADIUS + 0.5,
              BORDER_CORNER_RADIUS, -90 * degrees, 0 * degrees);

    cairo_arc(cr,
              area->x + area->width - BORDER_CORNER_RADIUS - 0.5,
              area->y + area->height - BORDER_CORNER_RADIUS - 0.5,
              BORDER_CORNER_RADIUS, 0 * degrees, 90 * degrees);

    cairo_arc(cr,
              area->x + BORDER_CORNER_RADIUS + 0.5,
              area->y + area->height - BORDER_CORNER_RADIUS - 0.5,
              BORDER_CORNER_RADIUS, 90 * degrees, 180 * degrees);

    cairo_arc(cr,
              area->x + BORDER_CORNER_RADIUS + 0.5,
              area->y + BORDER_CORNER_RADIUS + 0.5,
              BORDER_CORNER_RADIUS, 180 * degrees, 270 * degrees);

    cairo_close_path(cr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à venir consulter.                     *
*                cr    = contexte graphique associé à l'événement.            *
*                                                                             *
*  Description : Dessine si besoin est une bordure autour du composant.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_draw_border(GtkDisplayPanel *panel, cairo_t *cr)
{
    GtkWidget *widget;                      /* Autre version du composant  */
    GtkStyleContext *context;               /* Contexte du thème actuel    */
    GdkRGBA color;                          /* Couleur de thème récupérée  */
    GtkRequisition req;                     /* Taille allouée à l'élément  */
    GtkAllocation area;                     /* Emplacement à considérer    */

    if (panel->show_border)
    {
        widget = GTK_WIDGET(panel);

        gtk_widget_get_preferred_size(widget, NULL, &req);

        context = gtk_widget_get_style_context(widget);

        gtk_style_context_save(context);

        gtk_style_context_add_class(context, GTK_STYLE_CLASS_FRAME);

        gtk_style_context_get(gtk_widget_get_style_context(widget),
                              gtk_widget_get_state_flags(widget),
                              GTK_STYLE_PROPERTY_COLOR, &color, NULL);

        cairo_set_source_rgba(cr, color.red, color.green, color.blue, color.alpha);

        cairo_set_line_width(cr, 1.0);

        gtk_widget_get_preferred_size(GTK_WIDGET(panel), NULL, &req);

        area.x = 0;
        area.y = 0;
        area.width = req.width;
        area.height = req.height;

        gtk_display_panel_define_border_path(panel, cr, &area);
        cairo_stroke(cr);

        gtk_style_context_restore(context);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant GTK à consulter.                          *
*                cursor = emplacement à présenter à l'écran.                  *
*                x      = position horizontale au sein du composant. [OUT]    *
*                y      = position verticale au sein du composant. [OUT]      *
*                tweak  = adaptation finale à effectuer.                      *
*                                                                             *
*  Description : Indique la position d'affichage d'un emplacement donné.      *
*                                                                             *
*  Retour      : true si l'adresse fait partie du composant, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_display_panel_get_cursor_coordinates(const GtkDisplayPanel *panel, const GLineCursor *cursor, gint *x, gint *y, ScrollPositionTweak tweak)
{
    bool result;                            /* Bilan à remonter            */

    result = GTK_DISPLAY_PANEL_GET_CLASS(panel)->get_coordinates(panel, cursor, x, y, tweak);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                                                                             *
*  Description : Fournit l'élément actif lié à la position courante.          *
*                                                                             *
*  Retour      : Objet actif courant ou NULL si aucun.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *gtk_display_panel_get_active_object(const GtkDisplayPanel *panel)
{
    GObject *result;                        /* Trouvaille à retourner      */

    if (GTK_DISPLAY_PANEL_GET_CLASS(panel)->get_active == NULL)
        result = NULL;

    else
        result = GTK_DISPLAY_PANEL_GET_CLASS(panel)->get_active(panel);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à manipuler.                           *
*                addr  = adresse à présenter à l'écran.                       *
*                                                                             *
*  Description : Demande à qui veut répondre un déplacement du curseur.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_request_move(GtkDisplayPanel *panel, const vmpa2t *addr)
{
    GLineCursor *___tmp;

    ___tmp = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(___tmp), addr);

    g_loaded_panel_request_move(G_LOADED_PANEL(panel), ___tmp, false);

    g_object_unref(G_OBJECT(___tmp));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                event = informations liées à l'événement.                    *
*                                                                             *
*  Description : Transcrit les coordonnées à l'écran en coordonnées absolues. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_compute_fake_coord(GtkDisplayPanel *panel, gint *x, gint *y)
{
    if (panel->hadjustment != NULL)
        *x -= gtk_adjustment_get_value(panel->hadjustment);

    if (panel->vadjustment != NULL)
        *y += gtk_adjustment_get_value(panel->vadjustment);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                event = informations liées à l'événement.                    *
*                                                                             *
*  Description : Transcrit les coordonnées absolues en coordonnées à l'écran. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_compute_real_coord(GtkDisplayPanel *panel, gint *x, gint *y)
{
    if (x != NULL && panel->hadjustment != NULL)
        *x += gtk_adjustment_get_value(panel->hadjustment);

    if (y != NULL && panel->vadjustment != NULL)
        *y += gtk_adjustment_get_value(panel->vadjustment);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                x     = abscisse à ajuster. [OUT]                            *
*                x     = ordonnée à ajuster. [OUT]                            *
*                                                                             *
*  Description : Transcrit les coordonnées absolues en coordonnées à l'écran. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_display_panel_compute_relative_coords(GtkDisplayPanel *panel, gint *x, gint *y)
{
    if (x != NULL && panel->hadjustment != NULL)
        *x -= gtk_adjustment_get_value(panel->hadjustment);

    if (y != NULL && panel->vadjustment != NULL)
        *y -= gtk_adjustment_get_value(panel->vadjustment);

}



/* ---------------------------------------------------------------------------------- */
/*                         INTERFACE DE PANNEAU DE CHARGEMENT                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : options = options à mettre à jour.                           *
*                index   = indice de l'option concernée.                      *
*                value   = nouvelle valeur à intégrer.                        *
*                panel   = composant GTK à consulter.                         *
*                                                                             *
*  Description : Réagit à un changement des règles d'affichage.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_display_panel_option_change(GDisplayOptions *options, size_t index, bool value, GtkDisplayPanel *panel)
{
    gtk_widget_queue_resize(gtk_widget_get_parent(GTK_WIDGET(panel)));
    gtk_widget_queue_resize(GTK_WIDGET(panel));
    gtk_widget_queue_draw(GTK_WIDGET(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel   = composant GTK à mettre à jour.                     *
*                content = binaire associé à intégrer.                        *
*                                                                             *
*  Description : Associe à un panneau d'affichage un binaire chargé.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_set_content(GtkDisplayPanel *panel, GLoadedContent *content)
{
    panel->view_index = g_loaded_content_get_view_index(content, GTK_WIDGET(panel));

    panel->options = g_loaded_content_get_display_options(content, panel->view_index);

    panel->binary = G_LOADED_BINARY(content);

    g_signal_connect(panel->options, "value-changed", G_CALLBACK(on_display_panel_option_change), panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                                                                             *
*  Description : Fournit le contenu associé à un panneau de chargement.       *
*                                                                             *
*  Retour      : Contenu quelconque chargé en mémoire.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GLoadedContent *gtk_display_panel_get_content(const GtkDisplayPanel *panel)
{
    GLoadedContent *result;                 /* Contenu à retourner         */

    result = G_LOADED_CONTENT(panel->binary);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                                                                             *
*  Description : Fournit le position courante dans un panneau de chargement.  *
*                                                                             *
*  Retour      : Informations relatives à la position du curseur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GLineCursor *gtk_display_panel_get_cursor(const GtkDisplayPanel *panel)
{
    GLineCursor *result;                    /* Contenu à retourner         */

    result = GTK_DISPLAY_PANEL_GET_CLASS(panel)->get_cursor(panel);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant GTK à manipuler.                          *
*                cursor = emplacement à présenter à l'écran.                  *
*                tweak  = adaptation finale à effectuer.                      *
*                move   = doit-on déplacer le curseur à l'adresse indiquée ?  *
*                                                                             *
*  Description : S'assure qu'un emplacement donné est visible à l'écran.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_scroll_to_cursor(GtkDisplayPanel *panel, const GLineCursor *cursor, ScrollPositionTweak tweak, bool move)
{
    GtkWidget *parent;                      /* Support parent à valider    */
    GtkDisplayPanelClass *class;            /* Classe de l'instance        */
    gint x;                                 /* Abscisse à garantir         */
    gint y;                                 /* Ordonnée à garantir         */
    GtkWidget *viewport;                    /* Parent avec défilement      */
    GtkAdjustment *adj;                     /* Défilement à mettre à jour  */
    gdouble step_inc;                       /* Valeur d'un petit pas       */
    gdouble page_size;                      /* Taille de l'affichage       */
    double value;                           /* Valeur courante             */

    /**
     * Si une vue partielle se déplace via cette fonction, il faut potentiellement
     * rediriger l'appel vers la vue en graphiques parente.
     */

    parent = gtk_widget_get_parent(GTK_WIDGET(panel));
    parent = gtk_widget_get_parent(GTK_WIDGET(parent));

    if (GTK_IS_DISPLAY_PANEL(parent))
        panel = GTK_DISPLAY_PANEL(parent);

    class = GTK_DISPLAY_PANEL_GET_CLASS(panel);

    if (class->prepare != NULL)
        class->prepare(panel, cursor);

    if (gtk_display_panel_get_cursor_coordinates(panel, cursor, &x, &y, tweak))
    {
        viewport = gtk_widget_get_parent(GTK_WIDGET(panel));

        /* Eventuel défilement horizontal */

        g_object_get(G_OBJECT(viewport), "hadjustment", &adj, NULL);

        step_inc = gtk_adjustment_get_step_increment(adj);
        page_size = gtk_adjustment_get_page_size(adj);
        value = gtk_adjustment_get_value(adj);

        if (x < value)
            gtk_adjustment_set_value(adj, x);

        else if ((x + step_inc) > (value + page_size))
            gtk_adjustment_set_value(adj, x + step_inc - page_size);

        /* Eventuel défilement vertical */

        g_object_get(G_OBJECT(viewport), "vadjustment", &adj, NULL);

        step_inc = gtk_adjustment_get_step_increment(adj);
        page_size = gtk_adjustment_get_page_size(adj);
        value = gtk_adjustment_get_value(adj);

        if (y < value || tweak != SPT_RAW)
            gtk_adjustment_set_value(adj, y);

        else if ((y + step_inc) > (value + page_size))
            gtk_adjustment_set_value(adj, y + step_inc - page_size);

        /* Déplacement du curseur */

        if (move && gtk_display_panel_get_cursor_coordinates(panel, cursor, &x, &y, SPT_RAW))
            class->move_caret_to(panel, x, y);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à manipuler.                           *
*                cairo = assistant pour la création de rendus.                *
*                area  = taille de la surface réduite à disposition.          *
*                scale = échelle vis à vis de la taille réelle.               *
*                                                                             *
*  Description : Place en cache un rendu destiné à l'aperçu graphique rapide. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_display_panel_cache_glance(GtkDisplayPanel *panel, cairo_t *cairo, const GtkAllocation *area, double scale)
{
    if (GTK_DISPLAY_PANEL_GET_CLASS(panel)->cache_glance != NULL)
        GTK_DISPLAY_PANEL_GET_CLASS(panel)->cache_glance(panel, cairo, area, scale);

}
