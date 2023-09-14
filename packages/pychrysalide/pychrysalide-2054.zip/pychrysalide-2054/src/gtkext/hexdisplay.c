
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hexdisplay.c - affichage d'un contenu binaire sous forme hexadécimale
 *
 * Copyright (C) 2019 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "hexdisplay.h"


#include "gtkbufferdisplay-int.h"
#include "../core/columns.h"
#include "../core/params.h"
#include "../format/format.h"
#include "../glibext/generators/hex.h"



/* Composant d'affichage de contenu sous forme hexadécimale (instance) */
struct _GtkHexDisplay
{
    GtkBufferDisplay parent;                /* A laisser en premier        */

    GBufferCache *cache;                    /* Cache pour l'affichage      */
    GHexGenerator *generator;               /* Générateur à la volée       */

};

/* Composant d'affichage de contenu sous forme hexadécimale (classe) */
struct _GtkHexDisplayClass
{
    GtkBufferDisplayClass parent;           /* A laisser en premier        */

};


/* Procède à l'initialisation des afficheurs sous forme hexa. */
static void gtk_hex_display_class_init(GtkHexDisplayClass *);

/* Procède à l'initialisation de l'afficheur sous forme hexa. */
static void gtk_hex_display_init(GtkHexDisplay *);

/* Supprime toutes les références externes. */
static void g_hex_display_dispose(GtkHexDisplay *);

/* Procède à la libération totale de la mémoire. */
static void g_hex_display_finalize(GtkHexDisplay *);

/* S'adapte à la surface concédée par le composant parent. */
static void gtk_hex_display_size_allocate(GtkWidget *, GtkAllocation *);

/* Indique les dimensions de travail du composant d'affichage. */
static void gtk_hex_display_compute_requested_size(GtkHexDisplay *, gint *, gint *);

/* Adapte le cache de lignes hexadécimales à la taille courante. */
static void gtk_hex_display_populate_cache(GtkHexDisplay *);



/* Détermine le type du composant d'affichage sous forme hexadécimale. */
G_DEFINE_TYPE(GtkHexDisplay, gtk_hex_display, GTK_TYPE_BUFFER_DISPLAY)


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Procède à l'initialisation des afficheurs sous forme hexa.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_hex_display_class_init(GtkHexDisplayClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GtkWidgetClass *widget_class;           /* Classe de haut niveau       */
    GtkDisplayPanelClass *panel_class;      /* Classe parente              */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_hex_display_dispose;
    object->finalize = (GObjectFinalizeFunc)g_hex_display_finalize;

    widget_class = GTK_WIDGET_CLASS(class);

    widget_class->size_allocate = gtk_hex_display_size_allocate;

    panel_class = GTK_DISPLAY_PANEL_CLASS(class);

    panel_class->compute_size = (compute_requested_size_fc)gtk_hex_display_compute_requested_size;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = composant GTK à initialiser.                          *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur sous forme hexa.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_hex_display_init(GtkHexDisplay *view)
{

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

static void g_hex_display_dispose(GtkHexDisplay *display)
{
    g_clear_object(&display->cache);

    g_clear_object(&display->generator);

    G_OBJECT_CLASS(gtk_hex_display_parent_class)->dispose(G_OBJECT(display));

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

static void g_hex_display_finalize(GtkHexDisplay *display)
{
    G_OBJECT_CLASS(gtk_hex_display_parent_class)->finalize(G_OBJECT(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu brut à représenter.                        *
*                                                                             *
*  Description : Crée un nouveau composant pour l'affichage sous forme hexa.  *
*                                                                             *
*  Retour      : Composant GTK créé.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_hex_display_new(GBinContent *content)
{
    GtkHexDisplay *result;                  /* Composant à retourner       */
    GBufferView *view;                      /* Vue pointée sur un tampon   */
    int padding;                            /* Bourrage entre colonnes     */
    GWidthTracker *tracker;                 /* Gestionnaire de largeurs    */

    result = g_object_new(GTK_TYPE_HEX_DISPLAY, NULL);

    result->cache = g_buffer_cache_new(content, HLC_COUNT, HLC_BINARY);
    g_object_ref_sink(G_OBJECT(result->cache));

    g_generic_config_get_value(get_main_configuration(), MPK_HEX_PADDING, &padding);

    tracker = g_buffer_cache_get_width_tracker(result->cache);
    g_width_tracker_set_column_min_width(tracker, HLC_PADDING, padding);
    g_object_unref(G_OBJECT(tracker));

    result->generator = g_hex_generator_new(content);

    gtk_hex_display_populate_cache(result);

    view = g_buffer_view_new(result->cache, NULL);

    GTK_BUFFER_DISPLAY(result)->view = view;

    return GTK_WIDGET(result);

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

static void gtk_hex_display_size_allocate(GtkWidget *widget, GtkAllocation *allocation)
{
    GtkHexDisplay *display;                 /* Autre version du composant  */
    GBufferCache *cache;                    /* Contenu représenté          */
    gint text_pos;                          /* Abscisse minimale du texte  */
    bool show_pos;                          /* Affichage des positions ?   */
    GWidthTracker *tracker;                 /* Gestionnaire de largeurs    */
    gint padding;                           /* Bourrage supplémentaire     */
    bool changed;                           /* Note toute variation        */

    display = GTK_HEX_DISPLAY(widget);

    cache = g_buffer_view_get_cache(GTK_BUFFER_DISPLAY(display)->view);
    text_pos = g_buffer_cache_get_text_position(cache);
    g_object_unref(G_OBJECT(cache));

    show_pos = g_display_options_get(GTK_DISPLAY_PANEL(widget)->options, 0);

    tracker = g_buffer_cache_get_width_tracker(display->cache);
    padding = g_width_tracker_get_column_min_width(tracker, HLC_PADDING);
    g_object_unref(G_OBJECT(tracker));

    changed = g_hex_generator_auto_fit(display->generator, text_pos, show_pos, padding, allocation->width);

    if (changed)
        gtk_hex_display_populate_cache(display);

    /**
     * On fait appel au parent en dernier pour bénéficier des besoins
     * en espace actualisés avec les nouvelles dispositions.
     */

    GTK_WIDGET_CLASS(gtk_hex_display_parent_class)->size_allocate(widget, allocation);

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

static void gtk_hex_display_compute_requested_size(GtkHexDisplay *display, gint *width, gint *height)
{
    GtkDisplayPanel *pdisplay;              /* Version parente             */

    pdisplay = GTK_DISPLAY_PANEL(display);

    GTK_DISPLAY_PANEL_CLASS(gtk_hex_display_parent_class)->compute_size(pdisplay, width, height);

    if (width != NULL && *width != 0)
        *width = 1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à mettre à jour.                     *
*                                                                             *
*  Description : Adapte le cache de lignes hexadécimales à la taille courante.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_hex_display_populate_cache(GtkHexDisplay *display)
{
    GBinContent *content;                   /* Contenu binaire affiché     */
    phys_t full;                            /* Taille totale à représenter */
    phys_t line;                            /* Taille représentée par ligne*/
    size_t needed;                          /* Nombre de lignes nécessaires*/
    size_t count;                           /* Nombre actuel de lignes     */

    /* Détermination du besoin */

    content = g_hex_generator_get_content(display->generator);

    full = g_binary_content_compute_size(content);

    g_object_unref(G_OBJECT(content));

    line = g_hex_generator_get_bytes_per_line(display->generator);

    needed = full / line;

    if (full % line > 0)
        needed++;

    /* Adaptation du tampon interne */

    g_buffer_cache_wlock(display->cache);

    count = g_buffer_cache_count_lines(display->cache);

    if (needed < count)
        g_buffer_cache_truncate(display->cache, needed);

    else if (needed > count)
        g_buffer_cache_extend_with(display->cache, needed, G_LINE_GENERATOR(display->generator));

    g_buffer_cache_wunlock(display->cache);

    if (needed != count)
        gtk_widget_queue_resize(GTK_WIDGET(display));

}
