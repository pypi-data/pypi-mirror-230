
/* Chrysalide - Outil d'analyse de fichiers binaires
 * glance.c - panneau d'aperçu rapide
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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


#include "glance.h"


#include <string.h>
#include <gtk/gtk.h>


#include "../panel-int.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/named.h"



/* Panneau d'aperçu rapide (instance) */
struct _GGlancePanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GLoadedPanel *view;                     /* Vue à représenter           */
    GtkRequisition req;                     /* Pleine taille de la source  */
    GtkScrolledWindow *support;             /* Support défilant associé    */

    double scale;                           /* Ratio de réduction          */

	cairo_surface_t *cache;                 /* Cache grandeur nature       */
    GtkAllocation frame;                    /* Représentation du cadre     */
    GtkAllocation painting;                 /* Zone réservée pour l'aperçu */
    GtkAllocation visible;                  /* Sous-partie visible         */

    gdouble start_x;                        /* Abscisse du point de souris */
    gdouble start_y;                        /* Ordonnée du point de souris */
    bool valid;                             /* Point de départ visible ?   */
    gdouble ref_h;                          /* Position horizontale de ref.*/
    gdouble ref_v;                          /* Position verticale de ref.  */

};


/* Panneau d'aperçu rapide (classe) */
struct _GGlancePanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

    GtkIconInfo *no_image_32;               /* Pas d'aperçu en 32x32       */
    GtkIconInfo *no_image_64;               /* Pas d'aperçu en 64x64       */
    GtkIconInfo *no_image_128;              /* Pas d'aperçu en 128x128     */

};


/* Espace entre le cadre et l'aperçu */
#define GLANCE_BORDER 3


/* Initialise la classe des panneaux d'aperçu rapide. */
static void g_glance_panel_class_init(GGlancePanelClass *);

/* Initialise une instance de panneau d'aperçu rapide. */
static void g_glance_panel_init(GGlancePanel *);

/* Supprime toutes les références externes. */
static void g_glance_panel_dispose(GGlancePanel *);

/* Procède à la libération totale de la mémoire. */
static void g_glance_panel_finalize(GGlancePanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_glance_panel_class_get_key(const GGlancePanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_glance_panel_class_get_path(const GGlancePanelClass *);

/* Lance une actualisation du fait d'un changement de support. */
static void change_glance_panel_current_view(GGlancePanel *, GLoadedPanel *, GLoadedPanel *);

/* Réagit à la préparation du défilement du support original. */
static void on_view_scroll_setup(GtkAdjustment *, GGlancePanel *);

/* Réagit à un défilement du support original. */
static void on_view_scrolled(GtkAdjustment *, GGlancePanel *);

/* Réagit à un changement de taille de l'espace de rendu. */
static void on_glance_resize(GtkWidget *, GdkRectangle *, GGlancePanel *);

/* Calcule l'emplacement du rendu maniature et son échelle. */
static void compute_glance_scale(GGlancePanel *);

/* Lance une actualisation du fait d'un changement de vue. */
static void update_glance_panel_view(GGlancePanel *, GLoadedPanel *);

/* Met à jour l'affichage de l'aperçu rapide à présenter. */
static gboolean redraw_glance_area(GtkWidget *, cairo_t *, GGlancePanel *);

/* Assure la gestion des clics de souris sur l'aperçu. */
static gboolean on_button_press_over_glance(GtkWidget *, GdkEventButton *, GGlancePanel *);

/* Termine la gestion des clics de souris sur l'aperçu. */
static gboolean on_button_release_over_glance(GtkWidget *, GdkEventButton *, GGlancePanel *);

/* Assure la gestion du déplacement de la souris sur l'aperçu. */
static gboolean on_mouse_motion_over_glance(GtkWidget *, GdkEventMotion *, GGlancePanel *);



/* Indique le type défini pour un panneau d'aperçu rapide. */
G_DEFINE_TYPE(GGlancePanel, g_glance_panel, G_TYPE_PANEL_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'aperçu rapide.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_glance_panel_class_init(GGlancePanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/
    GtkIconTheme *theme;                    /* Thème GTK offrant des icones*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_glance_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_glance_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_glance_panel_class_get_key;

    item->change_view = (change_item_view_fc)change_glance_panel_current_view;
    item->update_view = (update_item_view_fc)update_glance_panel_view;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_path = (get_panel_path_fc)g_glance_panel_class_get_path;

    theme = gtk_icon_theme_get_default();

    class->no_image_32 = gtk_icon_theme_lookup_icon(theme, "image-missing", 32, GTK_ICON_LOOKUP_FORCE_SIZE);
    class->no_image_64 = gtk_icon_theme_lookup_icon(theme, "image-missing", 64, GTK_ICON_LOOKUP_FORCE_SIZE);
    class->no_image_128 = gtk_icon_theme_lookup_icon(theme, "image-missing", 128, GTK_ICON_LOOKUP_FORCE_SIZE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'aperçu rapide.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_glance_panel_init(GGlancePanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Glance"),
                                                                        _("Glimpse of the display content"),
                                                                        PANEL_GLANCE_ID));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(redraw_glance_area),
                                     BUILDER_CALLBACK(on_glance_resize),
                                     BUILDER_CALLBACK(on_button_press_over_glance),
                                     BUILDER_CALLBACK(on_button_release_over_glance),
                                     BUILDER_CALLBACK(on_mouse_motion_over_glance),
                                     NULL);

    gtk_builder_connect_signals(builder, panel);

    g_object_unref(G_OBJECT(builder));

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

static void g_glance_panel_dispose(GGlancePanel *panel)
{
    if (panel->cache != NULL)
        cairo_surface_destroy(panel->cache);

    G_OBJECT_CLASS(g_glance_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_glance_panel_finalize(GGlancePanel *panel)
{
    G_OBJECT_CLASS(g_glance_panel_parent_class)->finalize(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_glance_panel_class_get_key(const GGlancePanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_GLANCE_ID);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique le chemin initial de la localisation d'un panneau.   *
*                                                                             *
*  Retour      : Chemin fixé associé à la position initiale.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_glance_panel_class_get_path(const GGlancePanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("MEs");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau d'aperçu rapide.                             *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_glance_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_GLANCE_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau à actualiser.                                *
*                old   = ancienne vue du contenu chargé analysé.              *
*                new   = nouvelle vue du contenu chargé analysé.              *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de support.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_glance_panel_current_view(GGlancePanel *panel, GLoadedPanel *old, GLoadedPanel *new)
{
    GtkAdjustment *adj;                     /* Gestionnaire du défilement  */
    GtkWidget *parent;                      /* Support défilant de la vue  */

    if (panel->view != NULL)
    {
        g_object_unref(G_OBJECT(panel->view));
        panel->view = NULL;

        if (panel->support != NULL)
        {
            adj = gtk_scrolled_window_get_hadjustment(panel->support);
            g_signal_handlers_disconnect_by_func(adj, G_CALLBACK(on_view_scroll_setup), panel);
            g_signal_handlers_disconnect_by_func(adj, G_CALLBACK(on_view_scrolled), panel);

            adj = gtk_scrolled_window_get_vadjustment(panel->support);
            g_signal_handlers_disconnect_by_func(adj, G_CALLBACK(on_view_scroll_setup), panel);
            g_signal_handlers_disconnect_by_func(adj, G_CALLBACK(on_view_scrolled), panel);

            g_object_unref(G_OBJECT(panel->support));
            panel->support = NULL;

        }

        if (panel->cache != NULL)
        {
            cairo_surface_destroy(panel->cache);
            panel->cache = NULL;
        }

    }

    /**
     * Pour le détail de la hiérarchie, se retourner vers les commentaires
     * de la fonction mcb_view_change_support().
     */

    if (new != NULL)
    {
        parent = gtk_widget_get_parent(GTK_WIDGET(new));

        if (!GTK_IS_SCROLLED_WINDOW(parent))
        {
            panel->view = NULL;
            return;
        }

    }

    panel->view = new;

    if (panel->view != NULL)
    {
        g_object_ref(G_OBJECT(panel->view));

        panel->support = GTK_SCROLLED_WINDOW(parent);
        g_object_ref(G_OBJECT(panel->support));

        adj = gtk_scrolled_window_get_hadjustment(panel->support);
        g_signal_connect(G_OBJECT(adj), "changed", G_CALLBACK(on_view_scroll_setup), panel);
        g_signal_connect(G_OBJECT(adj), "value-changed", G_CALLBACK(on_view_scrolled), panel);

        adj = gtk_scrolled_window_get_vadjustment(panel->support);
        g_signal_connect(G_OBJECT(adj), "changed", G_CALLBACK(on_view_scroll_setup), panel);
        g_signal_connect(G_OBJECT(adj), "value-changed", G_CALLBACK(on_view_scrolled), panel);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : adj   = contrôle du défilement modifié.                      *
*                panel = panneau de l'aperçu à actualiser.                    *
*                                                                             *
*  Description : Réagit à la préparation du défilement du support original.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_view_scroll_setup(GtkAdjustment *adj, GGlancePanel *panel)
{
    GtkAdjustment *hadj;                    /* Gestionnaire du défilement  */
    GtkAdjustment *vadj;                    /* Gestionnaire du défilement  */

    hadj = gtk_scrolled_window_get_hadjustment(panel->support);
    vadj = gtk_scrolled_window_get_vadjustment(panel->support);

    if (gtk_adjustment_get_page_size(hadj) == 0 || gtk_adjustment_get_page_size(vadj) == 0)
        return;

    gtk_widget_get_preferred_size(GTK_WIDGET(panel->view), NULL, &panel->req);

    compute_glance_scale(panel);

    on_view_scrolled(adj, panel);

    update_glance_panel_view(panel, panel->view);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : adj   = contrôle du défilement modifié.                      *
*                panel = panneau de l'aperçu à actualiser.                    *
*                                                                             *
*  Description : Réagit à un défilement du support original.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_view_scrolled(GtkAdjustment *adj, GGlancePanel *panel)
{
    GtkAdjustment *hadj;                    /* Gestionnaire du défilement  */
    GtkAdjustment *vadj;                    /* Gestionnaire du défilement  */
    GtkWidget *widget;                      /* Surface de dessin pour GTK  */

    hadj = gtk_scrolled_window_get_hadjustment(panel->support);
    vadj = gtk_scrolled_window_get_vadjustment(panel->support);

    if (gtk_adjustment_get_page_size(hadj) == 0 || gtk_adjustment_get_page_size(vadj) == 0)
        return;

    panel->visible.x = panel->painting.x + gtk_adjustment_get_value(hadj) * panel->scale;
    panel->visible.y = panel->painting.y + gtk_adjustment_get_value(vadj) * panel->scale;
    panel->visible.width = gtk_adjustment_get_page_size(hadj) * panel->scale;
    panel->visible.height = gtk_adjustment_get_page_size(vadj) * panel->scale;

    widget = g_named_widget_get_widget(G_PANEL_ITEM(panel)->widget);

    gtk_widget_queue_draw(widget);

    g_object_unref(G_OBJECT(widget));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK ayant changé de taille.               *
*                alloc  = nouvel espace mis à disposition.                    *
*                panel  = panneau de l'aperçu à actualiser.                   *
*                                                                             *
*  Description : Réagit à un changement de taille de l'espace de rendu.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_glance_resize(GtkWidget *widget, GdkRectangle *allocation, GGlancePanel *panel)
{
    if (panel->view != NULL)
    {
        on_view_scroll_setup(NULL, panel);
        update_glance_panel_view(panel, panel->view);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau à actualiser.                                *
*                                                                             *
*  Description : Calcule l'emplacement du rendu maniature et son échelle.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void compute_glance_scale(GGlancePanel *panel)
{
    GtkWidget *widget;                      /* Surface de dessin pour GTK  */
    GtkAllocation available;                /* Surface disponible totale   */
    GtkAllocation granted;                  /* Surface totale accordée     */
    double sx;                              /* Echelle sur l'axe X         */
    double sy;                              /* Echelle sur l'axe Y         */

    /* Superficies niveau GTK... */

    widget = g_named_widget_get_widget(G_PANEL_ITEM(panel)->widget);

    gtk_widget_get_allocation(widget, &available);

    g_object_unref(G_OBJECT(widget));

    /* Calcul des ratios et emplacements */

    granted = available;

    if (available.width > 2 *  GLANCE_BORDER)
        granted.width = available.width - 2 *  GLANCE_BORDER;
    else
        granted.width = 0;

    if (available.height > 2 *  GLANCE_BORDER)
        granted.height = available.height - 2 *  GLANCE_BORDER;
    else
        granted.height = 0;

    sx = (1.0 * granted.width) / panel->req.width;
    sy = (1.0 * granted.height) / panel->req.height;

    /* Calcul des dimensions internes */

    if (sx < sy)
    {
        panel->scale = sx;
        panel->frame.width = available.width;
        panel->frame.height = panel->req.height * panel->scale;
    }
    else
    {
        panel->scale = sy;
        panel->frame.width = panel->req.width * panel->scale;
        panel->frame.height = available.height;
    }

    panel->frame.x = (available.width - panel->frame.width) / 2;
    panel->frame.y = (available.height - panel->frame.height) / 2;

    panel->painting.x = panel->frame.x + GLANCE_BORDER;
    panel->painting.y = panel->frame.y + GLANCE_BORDER;

    if (panel->frame.width > 2 *  GLANCE_BORDER)
        panel->painting.width = panel->frame.width - 2 *  GLANCE_BORDER;
    else
        panel->painting.width = 0;

    if (panel->frame.height > 2 * GLANCE_BORDER)
        panel->painting.height = panel->frame.height - 2 * GLANCE_BORDER;
    else
        panel->painting.height = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau à actualiser.                                *
*                view  = nouveau panneau d'affichage actif.                   *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de vue.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_glance_panel_view(GGlancePanel *panel, GLoadedPanel *view)
{
    cairo_t *cairo;                         /* Assistant pour le dessin    */
    GtkAllocation area;                     /* Dimension de la surface     */
    GtkWidget *widget;                      /* Surface de dessin pour GTK  */

    /* Mise en place d'un cache adapté */

    if (panel->cache != NULL)
        cairo_surface_destroy(panel->cache);

    panel->cache = cairo_image_surface_create(CAIRO_FORMAT_ARGB32,
                                              panel->painting.width,
                                              panel->painting.height);

    /* Dessin de l'aperçu représentatif */

    cairo = cairo_create(panel->cache);

    area.x = 0;
    area.y = 0;
    area.width = panel->painting.width;
    area.height = panel->painting.height;

    g_loaded_panel_cache_glance(view, cairo, &area, panel->scale);

    cairo_destroy(cairo);

    widget = g_named_widget_get_widget(G_PANEL_ITEM(panel)->widget);

    gtk_widget_queue_draw(widget);

    g_object_unref(G_OBJECT(widget));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à redessiner.                         *
*                cr     = contexte graphique liées à l'événement.             *
*                panel  = informations liées au panneau associé.              *
*                                                                             *
*  Description : Met à jour l'affichage de l'aperçu rapide à présenter.       *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean redraw_glance_area(GtkWidget *widget, cairo_t *cr, GGlancePanel *panel)
{
    GtkAllocation alloc;                    /* Surface disponible totale   */
    GdkWindow *window;                      /* Fenêtre à redessiner        */
    GtkStyleContext *context;               /* Contexte du thème actuel    */
    gint size;                              /* Taille d'icone à dessiner   */
    GtkIconInfo *no_image;                  /* Pas d'aperçu en XxX         */
    cairo_surface_t *icon;                  /* Eventuelle icone à dessiner */

    gtk_widget_get_allocation(widget, &alloc);

    window = gtk_widget_get_window(widget);

    cairo_save(cr);
    gtk_cairo_transform_to_window(cr, widget, window);

    context = gtk_widget_get_style_context(widget);
    gtk_style_context_save(context);

    /* S'il n'existe pas d'aperçu actuellement... */
    if (panel->cache == NULL)
    {
        gtk_style_context_add_class(context, GTK_STYLE_CLASS_VIEW);
        gtk_render_background(context, cr, alloc.x, alloc.y, alloc.width, alloc.height);
        gtk_style_context_restore(context);

        gtk_style_context_save(context);
        gtk_style_context_add_class(context, GTK_STYLE_CLASS_FRAME);
        gtk_render_frame(context, cr, alloc.x, alloc.y, alloc.width, alloc.height);

        /* Choix de l'image par défaut */

        if (alloc.width > 128 && alloc.height > 128)
        {
            size = 128;
            no_image = G_GLANCE_PANEL_GET_CLASS(panel)->no_image_128;
        }
        else if (alloc.width > 64 && alloc.height > 64)
        {
            size = 64;
            no_image = G_GLANCE_PANEL_GET_CLASS(panel)->no_image_64;
        }
        else if (alloc.width > 32 && alloc.height > 32)
        {
            size = 32;
            no_image = G_GLANCE_PANEL_GET_CLASS(panel)->no_image_32;
        }
        else
            no_image = NULL;

        /* Dessin de cette image */

        if (no_image != NULL)
        {
            icon = gtk_icon_info_load_surface(no_image, window, NULL);  

            gtk_render_icon_surface(context, cr, icon,
                                    (alloc.width - size) / 2,
                                    (alloc.height - size) / 2);

            cairo_surface_destroy(icon);

        }

    }

    /* Si on dispose de graphique à représenter... */
    else
    {
        /* Dessin d'un fond */

        gtk_style_context_save(context);
        gtk_style_context_add_class(context, GTK_STYLE_CLASS_VIEW);

        gtk_render_background(context, cr,
                              panel->frame.x, panel->frame.y,
                              panel->frame.width, panel->frame.height);

        gtk_style_context_restore(context);

        /* Dessin d'un cadre */

        gtk_style_context_save(context);
        gtk_style_context_add_class(context, GTK_STYLE_CLASS_FRAME);

        gtk_render_frame(context, cr,
                              panel->frame.x, panel->frame.y,
                              panel->frame.width, panel->frame.height);

        gtk_style_context_restore(context);

        /* Partie visible */

        cairo_rectangle(cr, panel->visible.x, panel->visible.y,
                        panel->visible.width, panel->visible.height);

        cairo_clip(cr);

        cairo_set_source_rgb(cr, 1.0, 1.0, 1.0);

        cairo_rectangle(cr, panel->painting.x, panel->painting.y,
                        panel->painting.width, panel->painting.height);

        cairo_fill(cr);

        cairo_reset_clip(cr);

        /* Aperçu mignature */

        cairo_set_source_surface(cr, panel->cache, panel->painting.x, panel->painting.y);
        cairo_paint(cr);

    }

    gtk_style_context_restore(context);

    cairo_restore(cr);

    return TRUE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                panel  = informations liées au panneau associé.              *
*                                                                             *
*  Description : Assure la gestion des clics de souris sur l'aperçu.          *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_button_press_over_glance(GtkWidget *widget, GdkEventButton *event, GGlancePanel *panel)
{
    GtkAdjustment *hadj;                    /* Gestionnaire du défilement  */
    GtkAdjustment *vadj;                    /* Gestionnaire du défilement  */
    GdkCursor *cursor;                      /* Pointeur pour la surface    */

    if (panel->view != NULL && event->button == 1)
    {
        panel->start_x = event->x;
        panel->start_y = event->y;

        hadj = gtk_scrolled_window_get_hadjustment(panel->support);
        vadj = gtk_scrolled_window_get_vadjustment(panel->support);

        panel->ref_h = gtk_adjustment_get_value(hadj);
        panel->ref_v = gtk_adjustment_get_value(vadj);

        panel->valid = (panel->visible.x <= panel->start_x
                        && panel->start_x < (panel->visible.x + panel->visible.width)
                        && panel->visible.y <= panel->start_y
                        && panel->start_y < (panel->visible.y + panel->visible.height));

        if (panel->valid)
        {
            cursor = gdk_cursor_new_for_display(gdk_display_get_default(), GDK_FLEUR);
            gdk_window_set_cursor(gtk_widget_get_window(widget), cursor);
            g_object_unref(G_OBJECT(cursor));
        }

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                panel  = informations liées au panneau associé.              *
*                                                                             *
*  Description : Termine la gestion des clics de souris sur l'aperçu.         *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_button_release_over_glance(GtkWidget *widget, GdkEventButton *event, GGlancePanel *panel)
{
    if (panel->view != NULL && event->button == 1)
    {
        if (panel->valid)
            gdk_window_set_cursor(gtk_widget_get_window(widget), NULL);

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                panel  = informations liées au panneau associé.              *
*                                                                             *
*  Description : Assure la gestion du déplacement de la souris sur l'aperçu.  *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_mouse_motion_over_glance(GtkWidget *widget, GdkEventMotion *event, GGlancePanel *panel)
{
    gdouble diff_x;                         /* Evolution sur les abscisses */
    gdouble diff_y;                         /* Evolution sur les ordonnées */
    GtkAdjustment *hadj;                    /* Gestionnaire du défilement  */
    GtkAdjustment *vadj;                    /* Gestionnaire du défilement  */
    gdouble value;                          /* Nouvelle valeur bornée      */

    if (panel->view != NULL && event->state & GDK_BUTTON1_MASK && panel->valid)
    {
        diff_x = (event->x - panel->start_x) / panel->scale;
        diff_y = (event->y - panel->start_y) / panel->scale;

        hadj = gtk_scrolled_window_get_hadjustment(panel->support);
        vadj = gtk_scrolled_window_get_vadjustment(panel->support);

        value = CLAMP(panel->ref_h + diff_x, gtk_adjustment_get_lower(hadj),
                      gtk_adjustment_get_upper(hadj) - gtk_adjustment_get_page_size(hadj));
        gtk_adjustment_set_value(hadj, value);

        value = CLAMP(panel->ref_v + diff_y, gtk_adjustment_get_lower(vadj),
                      gtk_adjustment_get_upper(vadj) - gtk_adjustment_get_page_size(vadj));
        gtk_adjustment_set_value(vadj, value);

    }

    return FALSE;

}
