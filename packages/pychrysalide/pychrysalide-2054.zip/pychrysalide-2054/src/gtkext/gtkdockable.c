
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdockable.c - éléments acceptés dans les composants de rassemblement
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "gtkdockable.h"


#include <assert.h>
#include <malloc.h>


#include <i18n.h>


#include "easygtk.h"
#include "gtkdockable-int.h"
#include "tmgt.h"
#include "../gui/agroup.h"



/* --------------------- DEFINITIONS PRINCIPALES DE L'INTERFACE --------------------- */


/* Procède à l'initialisation de l'interface de rassemblement. */
static void gtk_dockable_default_init(GtkDockableInterface *);

/* Applique un nouveau filtre sur un composant intégré. */
static void gtk_dockable_update_filter(GtkDockable *, const char *);



/* ------------------------ FONCTIONS DE RECHERCHE INTEGREES ------------------------ */


/* Construit une zone de recherches vouée à être intégrée. */
static GtkWidget *build_search_area(GtkDockable *, GtkWidget **);

/* Met à jour l'expression de filtrage de la zone intégrée. */
static void on_dockable_search_changed(GtkSearchEntry *, GtkDockable *);



/* ----------------------- PROCEDURES POUR LE GLISSER-DEPOSER ----------------------- */


/* Enumération des types de données à déplacer */

enum
{
    TARGET_ROOTWIN
};

static GtkTargetEntry target_list[] = {
    { "application/x-rootwindow-drop", 0, TARGET_ROOTWIN }
};


/* Fenêtre d'aperçu de destination */
static GtkWidget *_drag_window = NULL;

/* Dimensions maximales de l'aperçu du contenu déplacé */
#define DND_WND_MAX_WIDTH 250
#define DND_WND_MAX_HEIGHT 150

/* Emplacements de la fenêtre de DragAndDrop */

typedef enum _DNDWindowPosition
{
    DWP_NONE,                               /* Position non définie        */
    DWP_CENTER,                             /* Position centrale           */
    DWP_LEFT,                               /* Position à gauche           */
    DWP_TOP,                                /* Position supérieure         */
    DWP_RIGHT,                              /* Position à droite           */
    DWP_BOTTOM                              /* Position inférieure         */

} DNDWindowPosition;

static DNDWindowPosition _dnd_position = DWP_NONE;

/* Seuil de basculement entre zones */
#define BORDER_THRESHOLD 0.20


/* Amorce un démarrage de DragAndDrop. */
static void on_dockable_drag_begin(GtkWidget *, GdkDragContext *, void *);

/* Adapte le dessin de fond à de nouvelles dimensions. */
static void update_drag_window_background(GtkWidget *, gint, gint);

/* Suit le déplacement d'un contenu déposable. */
static gboolean on_dockable_drag_motion(GtkWidget *, GdkDragContext *, gint, gint, guint, void *);

/* Accommpagne la sortie de la souris d'un composant graphique. */
static void on_dockable_drag_leave(GtkWidget *, GdkDragContext *, guint, void *);



/* ---------------------------------------------------------------------------------- */
/*                       DEFINITIONS PRINCIPALES DE L'INTERFACE                       */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type d'une interface pour rassemblement. */
G_DEFINE_INTERFACE(GtkDockable, gtk_dockable, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GTK à initialiser.                         *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de rassemblement.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_dockable_default_init(GtkDockableInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Fournit le nom court du composant encapsulable.              *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *gtk_dockable_get_name(const GtkDockable *dockable)
{
    char *result;                           /* Désignation à retourner     */
    GtkDockableIface *iface;                /* Interface utilisée          */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    result = iface->get_name(dockable);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Fournit le nom long du composant encapsulable.               *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *gtk_dockable_get_desc(const GtkDockable *dockable)
{
    char *result;                           /* Description à retourner     */
    GtkDockableIface *iface;                /* Interface utilisée          */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    result = iface->get_desc(dockable);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Indique si le composant représenté à du contenu à fouiller.  *
*                                                                             *
*  Retour      : Etat de la capacité.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_dockable_can_search(const GtkDockable *dockable)
{
    bool result;                            /* Indication à retourner      */
    GtkDockableIface *iface;                /* Interface utilisée          */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    result = iface->can_search(dockable);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Fournit le composant graphique intégrable dans un ensemble.  *
*                                                                             *
*  Retour      : Composant graphique prêt à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_dockable_build_widget(GtkDockable *dockable)
{
    GtkWidget *result;                      /* Composant à retourner       */
    GtkDockableIface *iface;                /* Interface utilisée          */
    GtkWidget *widget;                      /* Composant graphique interne */
    GtkWidget *revealer;                    /* Révélateur à intégrer ?     */
    GtkWidget *search;                      /* Zone de recherche           */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    widget = iface->get_widget(dockable);

    /* Encapsulation avec un panneau coulissant ? */

    if (gtk_dockable_can_search(dockable))
    {
        revealer = gtk_revealer_new();
        gtk_widget_show(revealer);

        gtk_container_add(GTK_CONTAINER(revealer), build_search_area(dockable, &search));

        result = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
        gtk_widget_show(result);

        gtk_box_pack_start(GTK_BOX(result), revealer, FALSE, TRUE, 0);
        gtk_box_pack_start(GTK_BOX(result), widget, TRUE, TRUE, 0);

        g_object_set_data(G_OBJECT(result), "revealer", revealer);
        g_object_set_data(G_OBJECT(result), "search", search);

    }

    /* Ou bien non ! */
    else
        result = widget;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à manipuler.    *
*                filter   = nouveau filtre à appliquer.                       *
*                                                                             *
*  Description : Applique un nouveau filtre sur un composant intégré.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_dockable_update_filter(GtkDockable *dockable, const char *filter)
{
    GtkDockableIface *iface;                /* Interface utilisée          */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    iface->update_filtered(dockable, filter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                support  = composant à partir duquel décrocher ou NULL. [OUT]*
*                                                                             *
*  Description : Fournit tous les éléments pour un retrait graphique.         *
*                                                                             *
*  Retour      : Composant graphique à décrocher.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_dockable_decompose(GtkDockable *dockable, GtkWidget **support)
{
    GtkWidget *result;                      /* Composant à retourner       */
    GtkDockableIface *iface;                /* Interface utilisée          */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    result = iface->get_widget(dockable);

    if (gtk_dockable_can_search(dockable))
        result = gtk_widget_get_parent(result);     /* GtkBox */

    if (support != NULL)
        *support = gtk_widget_get_parent(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                built    = composant graphique d'encapsulation mis en place. *
*                reveal   = détermine l'action à mener.                       *
*                                                                             *
*  Description : Révèle ou cache la zone de recherches.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_dockable_toggle_revealer(GtkDockable *dockable, GtkWidget *built, gboolean reveal)
{
    GtkRevealer *revealer;                  /* Révélateur à actionner      */
    GtkWidget *entry;                       /* Zone de recherche à activer */

    revealer = GTK_REVEALER(g_object_get_data(G_OBJECT(built), "revealer"));
    assert(revealer != NULL);

    gtk_revealer_set_reveal_child(revealer, reveal);

    if (reveal)
    {
        entry = GTK_WIDGET(g_object_get_data(G_OBJECT(built), "search"));
        gtk_widget_grab_focus(entry);
    }

}



/* ---------------------------------------------------------------------------------- */
/*                          FONCTIONS DE RECHERCHE INTEGREES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = élément encapsulable à avertir des changements.   *
*                search   = zone de saisie pour lancer les recherches.        *
*                                                                             *
*  Description : Construit une zone de recherches vouée à être intégrée.      *
*                                                                             *
*  Retour      : Composant GTK prêt à être intégré.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *build_search_area(GtkDockable *dockable, GtkWidget **search)
{
    GtkWidget *result;                      /* Support à retourner         */
    GtkWidget *label;                       /* Etiquette à utiliser        */

    result = gtk_grid_new();
    gtk_grid_set_row_spacing(GTK_GRID(result), 8);
    gtk_widget_show(result);

    label = qck_create_label(NULL, NULL, _("Look for:"));
    g_object_set(label, "margin", 8, NULL);
    gtk_grid_attach(GTK_GRID(result), label, 0, 0, 1, 1);

    *search = gtk_search_entry_new();
    g_signal_connect(*search, "search-changed", G_CALLBACK(on_dockable_search_changed), dockable);
    g_signal_connect(*search, "focus-in-event", G_CALLBACK(track_focus_change_in_text_area), NULL);
    g_signal_connect(*search, "focus-out-event", G_CALLBACK(track_focus_change_in_text_area), NULL);
    gtk_widget_set_hexpand(*search, TRUE);
    gtk_widget_show(*search);
    gtk_grid_attach_next_to(GTK_GRID(result), *search, label, GTK_POS_RIGHT, 1, 1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry    = entrée de texte contenant le filtre brut.         *
*  Paramètres  : dockable = élément encapsulable à avertir des changements.   *
*                                                                             *
*  Description : Met à jour l'expression de filtrage de la zone intégrée.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dockable_search_changed(GtkSearchEntry *entry, GtkDockable *dockable)
{
    char *filter;                           /* Nouveau filtre à considérer */

    filter = NULL;

    update_regex_on_search_entry_changed(entry, &filter);

    gtk_dockable_update_filter(dockable, filter);

    free(filter);

}



/* ---------------------------------------------------------------------------------- */
/*                         PROCEDURES POUR LE GLISSER-DEPOSER                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prépare en sous-main la fenêtre de prédiction du déposer.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void prepare_drag_and_drop_window(void)
{
    GdkScreen *screen;                      /* Ecran d'affichage           */
    GdkVisual *rgba_visual;                 /* Configuration visuelle      */
    gboolean has_rgba;                      /* Support de la transparence ?*/

    screen = gdk_screen_get_default();
    rgba_visual = gdk_screen_get_rgba_visual(screen);

    has_rgba = (rgba_visual != NULL && gdk_screen_is_composited(screen));

    _drag_window = gtk_window_new(GTK_WINDOW_POPUP);

    if (has_rgba)
        gtk_widget_set_visual(_drag_window, rgba_visual);

    gtk_window_set_type_hint(GTK_WINDOW(_drag_window), GDK_WINDOW_TYPE_HINT_DND);
    gtk_window_set_screen(GTK_WINDOW(_drag_window), screen);

    gtk_widget_set_app_paintable(_drag_window, TRUE);

    gtk_widget_set_size_request(_drag_window, 1, 1);
    gtk_widget_realize(_drag_window);

    /**
     * Cf. commentaires de on_dockable_drag_leave().
     */
    gtk_window_resize(GTK_WINDOW(_drag_window), 1, 1);
    gtk_window_move(GTK_WINDOW(_drag_window), -1, -1);

    gtk_widget_show(_drag_window);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance de composant à intégrer pleinement.      *
*                                                                             *
*  Description : Initialise les fonctions de glisser/déposer pour un élément. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_dockable_setup_dnd(GtkDockable *dockable)
{
    GtkDockableIface *iface;                /* Interface utilisée          */
    GtkWidget *widget;                      /* Composant graphique interne */

    iface = GTK_DOCKABLE_GET_IFACE(dockable);

    widget = iface->get_widget(dockable);

#if 0
    gtk_drag_source_set(widget, GDK_BUTTON1_MASK,
                        target_list, G_N_ELEMENTS(target_list),
                        GDK_ACTION_MOVE);
#endif

    g_signal_connect_after(widget, "drag-begin", G_CALLBACK(on_dockable_drag_begin), NULL);

    gtk_drag_dest_set(widget, 0, target_list, G_N_ELEMENTS(target_list), GDK_ACTION_MOVE);

    g_signal_connect(widget, "drag-motion", G_CALLBACK(on_dockable_drag_motion), NULL);
    g_signal_connect(widget, "drag-leave", G_CALLBACK(on_dockable_drag_leave), NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique à l'origine de l'opération.    *
*                context = contexte assurant la gestion de l'opération.       *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Amorce un démarrage de DragAndDrop.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dockable_drag_begin(GtkWidget *widget, GdkDragContext *context, void *unused)
{
    GtkAllocation alloc;                    /* Espace graphique occupé     */
    gint width;                             /* Largeur de l'aperçu         */
    gint height;                            /* Hauteur de l'aperçu         */
    cairo_surface_t *surface;               /* Représentation du contenu   */
    cairo_t *cr;                            /* Pinceau de dessin           */
    GtkStyleContext *style;                 /* Contexte du thème actuel    */

    gtk_widget_get_allocation(widget, &alloc);

    if (alloc.width > alloc.height)
    {
        width = DND_WND_MAX_WIDTH;
        height = alloc.height * ((1.0 * DND_WND_MAX_WIDTH) / alloc.width);
    }
    else
    {
        height = DND_WND_MAX_HEIGHT;
        width = alloc.width * ((1.0 * DND_WND_MAX_HEIGHT) / alloc.height);
    }

    surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height);

    cr = cairo_create(surface);

    /* Fond */

    style = gtk_widget_get_style_context(widget);

    gtk_style_context_save(style);

    gtk_style_context_add_class(style, GTK_STYLE_CLASS_VIEW);

    gtk_render_background(style, cr, 0, 0, width, height);
    gtk_render_frame(style, cr, 0, 0, width, height);

    gtk_style_context_restore(style);

    /* Aperçu */

    cairo_save(cr);

    cairo_scale(cr, (1.0 * width) / alloc.width, (1.0 * height) / alloc.height);

    gtk_widget_draw(widget, cr);

    cairo_restore(cr);

    /* Application */

    gtk_drag_set_icon_surface(context, surface);

    cairo_destroy(cr);
    cairo_surface_destroy(surface);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dnd_widget = composant GTK assurant l'affichage du fond.     *
*                width      = nouvelle largeur à remplir.                     *
*                height     = nouvelle hauteur à remplir.                     *
*                                                                             *
*  Description : Adapte le dessin de fond à de nouvelles dimensions.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_drag_window_background(GtkWidget *dnd_window, gint width, gint height)
{
    GdkWindow *window;                      /* Représentation de bas niveau*/
    cairo_surface_t *surface;               /* Surface à appliquer au fond */
    cairo_t *cr;                            /* Pinceau de dessin           */
    GdkScreen *screen;                      /* Ecran d'affichage           */
    gboolean has_rgba;                      /* Support de la transparence ?*/
    cairo_surface_t *saturated;             /* Surface de remplacement     */
    cairo_region_t *region;                 /* Limites du dessin           */
    cairo_pattern_t *pattern;               /* Modèle de dessin final      */
    cairo_matrix_t matrix;                  /* Matrice de transformation   */

    window = gtk_widget_get_window(dnd_window);

    /**
     * Code inspiré de celui de la fonction gtk_drag_set_icon_surface().
     */

    /* Création d'un nouveau modèle */

    surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, width, height);

    cr = cairo_create(surface);

    cairo_set_source_rgba(cr, 1.0, 1.0, 1.0, 0.05);

    cairo_rectangle(cr, 0, 0, width, height);
    cairo_fill(cr);

    cairo_set_source_rgba(cr, 0.0, 0.0, 0.0, 0.05);

    cairo_rectangle(cr, 0, 0, width, height);
    cairo_stroke(cr);

    cairo_destroy(cr);

    /* Application */

    screen = gdk_window_get_screen(window);

    has_rgba = (gdk_screen_get_rgba_visual(screen) != NULL
                && gdk_screen_is_composited(screen));

    if (cairo_surface_get_content(surface) != CAIRO_CONTENT_COLOR && !has_rgba)
    {
        region = gdk_cairo_region_create_from_surface(surface);

        gtk_widget_shape_combine_region(dnd_window, region);
        cairo_region_destroy(region);

        saturated = gdk_window_create_similar_surface(window, CAIRO_CONTENT_COLOR, width, height);

        cr = cairo_create(saturated);
        cairo_push_group_with_content(cr, CAIRO_CONTENT_COLOR_ALPHA);
        cairo_set_source_surface(cr, surface, 0, 0);
        cairo_paint(cr);
        cairo_set_operator(cr, CAIRO_OPERATOR_SATURATE);
        cairo_paint(cr);
        cairo_pop_group_to_source(cr);
        cairo_paint(cr);
        cairo_destroy(cr);

        pattern = cairo_pattern_create_for_surface(saturated);

        cairo_surface_destroy(saturated);

    }
    else
    {
        pattern = cairo_pattern_create_for_surface(surface);
        cairo_matrix_init_translate(&matrix, 0, 0);
        cairo_pattern_set_matrix(pattern, &matrix);
    }

    cairo_surface_destroy(surface);

    // Deprecated
    // gdk_window_set_background_pattern(window, pattern);
    cairo_pattern_destroy(pattern);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique à l'origine de l'opération.    *
*                context = contexte assurant la gestion de l'opération.       *
*                x       = abscisse courante du pointeur de la souris.        *
*                y       = ordonnée courante du pointeur de la souris.        *
*                time    = horodatage associé à l'événement.                  *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Suit le déplacement d'un contenu déposable.                  *
*                                                                             *
*  Retour      : TRUE pour un contenu acceptable, FALSE sinon.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_dockable_drag_motion(GtkWidget *widget, GdkDragContext *context, gint x, gint y, guint time, void *unused)
{
    GtkAllocation alloc;                    /* Espace graphique occupé     */
    DNDWindowPosition wpos;                 /* Direction actuelle          */
    gint border_width;                      /* Largeur d'une bordure       */
    gint border_height;                     /* Hauteur d'une bordure       */
    gint corner_left;                       /* Bordure à gauche            */
    gint corner_top;                        /* Bordure en haut             */
    gint corner_right;                      /* Bordure à droite            */
    gint corner_bottom;                     /* Bordure en bas              */
    GtkAllocation update;                   /* Nouvelle position           */

    /* Détermination de la position idéale */

    gtk_widget_get_allocation(widget, &alloc);

    wpos = DWP_NONE;

    border_width = alloc.width * BORDER_THRESHOLD;
    border_height = alloc.height * BORDER_THRESHOLD;

    corner_left = border_width;
    corner_top = border_height;
    corner_right = alloc.width - border_width;
    corner_bottom = alloc.height - border_height;

    if (alloc.width > alloc.height)
    {
        if (x < corner_left)
            wpos = DWP_LEFT;
        else if (x > corner_right)
            wpos = DWP_RIGHT;
        else if (y < corner_top)
            wpos = DWP_TOP;
        else if (y > corner_bottom)
            wpos = DWP_BOTTOM;
    }
    else
    {
        if (y < corner_top)
            wpos = DWP_TOP;
        else if (y > corner_bottom)
            wpos = DWP_BOTTOM;
        else if (x < corner_left)
            wpos = DWP_LEFT;
        else if (x > corner_right)
            wpos = DWP_RIGHT;
    }

    if (x >= corner_left && x <= corner_right && y >= corner_top && y <= corner_bottom)
    {
        wpos = DWP_CENTER;
    }

    /* Mise à jour de la fenêtre de portée ? */

    if (_dnd_position != wpos)
    {
        if (wpos != DWP_NONE)
            gdk_window_get_origin(gtk_widget_get_window(widget), &update.x, &update.y);

        update.x += alloc.x;
        update.y += alloc.y;

        switch (wpos)
        {
            case DWP_NONE:
                break;

            case DWP_CENTER:
                update.x += border_width;
                update.y += border_height;
                update.width = alloc.width - 2 * border_width;
                update.height = alloc.height - 2 * border_height;
                break;

            case DWP_LEFT:
                update.width = border_width;
                update.height = alloc.height;
                break;

            case DWP_TOP:
                update.width = alloc.width;
                update.height = border_height;
                break;

            case DWP_RIGHT:
                update.x += corner_right;
                update.width = border_width;
                update.height = alloc.height;
                break;

            case DWP_BOTTOM:
                update.y += corner_bottom;
                update.width = alloc.width;
                update.height = border_height;
                break;

        }

        if (wpos == DWP_NONE)
        {
            /**
             * Cf. commentaires de on_dockable_drag_leave().
             */
            gtk_window_resize(GTK_WINDOW(_drag_window), 1, 1);
            gtk_window_move(GTK_WINDOW(_drag_window), -1, -1);
        }

        else
        {
            update_drag_window_background(_drag_window, update.width, update.height);

            gtk_window_move(GTK_WINDOW(_drag_window), update.x, update.y);
            gtk_window_resize(GTK_WINDOW(_drag_window), update.width, update.height);

        }

        _dnd_position = wpos;

    }

    gdk_drag_status(context, GDK_ACTION_MOVE, time);

    return TRUE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique qui était survolé.             *
*                context = contexte assurant la gestion de l'opération.       *
*                time    = horodatage associé à l'événement.                  *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Accommpagne la sortie de la souris d'un composant graphique. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dockable_drag_leave(GtkWidget *widget, GdkDragContext *context, guint time, void *unused)
{
    /**
     * Visiblement, cacher et réafficher la fenêtre d'aperçu de la zone de
     * destination provoque un enchaînement ininterrompu d'événements
     * "motion" & "leave".
     *
     * Conséquence : la fenêtre scintille.
     *
     * On contourne le bogue visuel en ne cachant plus la fenêtre.
     */

    _dnd_position = DWP_NONE;

    gtk_window_resize(GTK_WINDOW(_drag_window), 1, 1);
    gtk_window_move(GTK_WINDOW(_drag_window), -1, -1);

}
