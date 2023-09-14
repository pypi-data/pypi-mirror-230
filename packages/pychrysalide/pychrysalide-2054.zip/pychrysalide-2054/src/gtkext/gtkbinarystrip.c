
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkbinarystrip.c - affichage d'un binaire sous forme de bande
 *
 * Copyright (C) 2013-2018 Cyrille Bagard
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


#include "gtkbinarystrip.h"


#include "../glibext/chrysamarshal.h"



/* Affichage d'un binaire en bande (instance) */
struct _GtkBinaryStrip
{
    GtkDrawingArea parent;                  /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire à représenter       */
    gint display_pos;                       /* Position à l'écran          */

    vmpa2t cursor_addr;                     /* Adresse de la position      */
    gint cursor_pos;                        /* Position à l'écran          */

};

/* Affichage d'un binaire en bande (classe) */
struct _GtkBinaryStripClass
{
    GtkDrawingAreaClass parent;             /* A laisser en premier        */

    void (* select_address) (GtkBinaryStrip *);

};


/* Taille de l'encoche pour la position */
#define STRIP_MARKER_SIZE 7


/* Procède à l'initialisation de l'afficheur générique. */
static void gtk_binary_strip_class_init(GtkBinaryStripClass *);

/* Procède à l'initialisation de l'afficheur générique. */
static void gtk_binary_strip_init(GtkBinaryStrip *);

/* Encadre la préparation à l'affichage du composant. */
static void gtk_binary_strip_realize(GtkWidget *);

/* Réagit à un changement de taille du composant. */
static void gtk_binary_strip_size_allocate(GtkWidget *, GtkAllocation *);

/* Suit la progression de la souris sur le composant. */
static gboolean gtk_binary_strip_button_release(GtkWidget *, GdkEventButton *);

/* Met à jour l'affichage du composant d'affichage. */
static gboolean gtk_binary_strip_draw(GtkWidget *, cairo_t *);

/* Prépare l'affichage d'une astuce. */
static gboolean gtk_binary_strip_query_tooltip(GtkWidget *, gint, gint, gboolean, GtkTooltip *);



/* Détermine le type du composant d'affichage générique. */
G_DEFINE_TYPE(GtkBinaryStrip, gtk_binary_strip, GTK_TYPE_DRAWING_AREA)


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

static void gtk_binary_strip_class_init(GtkBinaryStripClass *class)
{
    GtkWidgetClass *widget_class;           /* Classe de haut niveau       */

    widget_class = GTK_WIDGET_CLASS(class);

    widget_class->realize = gtk_binary_strip_realize;
    widget_class->size_allocate = gtk_binary_strip_size_allocate;
    widget_class->button_release_event = gtk_binary_strip_button_release;
    widget_class->draw = gtk_binary_strip_draw;
    widget_class->query_tooltip = gtk_binary_strip_query_tooltip;

    g_signal_new("select-address",
                 GTK_TYPE_BINARY_STRIP,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkBinaryStripClass, select_address),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : strip = composant GTK à initialiser.                         *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur générique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_binary_strip_init(GtkBinaryStrip *strip)
{
    GObject *object;                        /* Autre version de l'instance */
    GtkWidget *widget;                      /* Autre version de l'instance */

    object = G_OBJECT(strip);
    widget = GTK_WIDGET(strip);

    g_object_set(object, "has-tooltip", TRUE, NULL);

    gtk_widget_set_size_request(widget, 400, 30);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau composant pour l'affichage d'une bande.      *
*                                                                             *
*  Retour      : Composant GTK créé.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_binary_strip_new(void)
{
    GtkBinaryStrip *result;                 /* Composant à retourner       */

    result = g_object_new(GTK_TYPE_BINARY_STRIP, NULL);

    return GTK_WIDGET(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à préparer.                           *
*                                                                             *
*  Description : Encadre la préparation à l'affichage du composant.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_binary_strip_realize(GtkWidget *widget)
{
    GdkCursor *cursor;                      /* Pointeur pour la surface    */

    GTK_WIDGET_CLASS(gtk_binary_strip_parent_class)->realize(widget);

    cursor = gdk_cursor_new_for_display(gdk_display_get_default(), GDK_HAND1);
    gdk_window_set_cursor(gtk_widget_get_window(widget), cursor);
    g_object_unref(cursor);

    gtk_widget_add_events(widget, GDK_BUTTON_PRESS_MASK | GDK_BUTTON_RELEASE_MASK);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget     = composant GTK à préparer.                       *
*                allocation = nouvelle taille à considérer.                   *
*                                                                             *
*  Description : Réagit à un changement de taille du composant.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_binary_strip_size_allocate(GtkWidget *widget, GtkAllocation *allocation)
{
    GtkBinaryStrip *strip;                  /* Autre version du composant  */
    GExeFormat *format;                     /* Format du binaire           */
    GBinPortion *portions;                  /* Couche première de portions */
    GdkRectangle area;                      /* Surface du composant        */

    GTK_WIDGET_CLASS(gtk_binary_strip_parent_class)->size_allocate(widget, allocation);

    strip = GTK_BINARY_STRIP(widget);

    if (strip->binary == NULL)
        return;

    format = g_loaded_binary_get_format(strip->binary);
    portions = g_exe_format_get_portions(format);

    area.x = 0;
    area.y = 0;
    area.width = allocation->width;
    area.height = allocation->height;

    if (!get_binary_portion_pos_from_addr(portions, &strip->cursor_addr, &area, &strip->cursor_pos))
        strip->cursor_pos = 0;

    g_object_unref(G_OBJECT(portions));
    g_object_unref(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                                                                             *
*  Description : Suit la progression de la souris sur le composant.           *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_binary_strip_button_release(GtkWidget *widget, GdkEventButton *event)
{
    gint width;                             /* Laugeur du composant        */
    gint height;                            /* Hauteur du composant        */
    GtkBinaryStrip *strip;                  /* Autre version du composant  */
    GExeFormat *format;                     /* Format du binaire           */
    GBinPortion *portions;                  /* Couche première de portions */
    GdkRectangle area;                      /* Surface du composant        */
    vmpa2t addr;                            /* Adresse à sélectionner      */

    if (event->x < 0 || event->y < 0)
        return FALSE;

    width = gtk_widget_get_allocated_width(widget);
    height = gtk_widget_get_allocated_height(widget);

    if (event->x >= width || event->y >= height)
        return FALSE;

    strip = GTK_BINARY_STRIP(widget);
    format = g_loaded_binary_get_format(strip->binary);
    portions = g_exe_format_get_portions(format);

    area.x = 0;
    area.y = 0;
    area.width = width;
    area.height = height;

    if (get_binary_portion_addr_from_pos(portions, event->x, &area, &addr))
    {
        copy_vmpa(&strip->cursor_addr, &addr);
        strip->cursor_pos = event->x;

        gtk_widget_queue_draw(GTK_WIDGET(strip));

        g_signal_emit_by_name(strip, "select-address");

    }

    g_object_unref(G_OBJECT(portions));
    g_object_unref(G_OBJECT(format));

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à redessiner.                         *
*                cr     = contexte graphique associé à l'événement.           *
*                                                                             *
*  Description : Met à jour l'affichage du composant d'affichage.             *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_binary_strip_draw(GtkWidget *widget, cairo_t *cr)
{
    GtkBinaryStrip *strip;                  /* Autre vision du composant   */
    GtkStyleContext *context;               /* Contexte du thème actuel    */
    GExeFormat *format;                     /* Format du binaire           */
    GBinPortion *portions;                  /* Portions de binaire         */
    GdkRectangle full;                      /* Taille totale de la surface */
    GdkRGBA *color;                         /* Couleur du curseur          */

    strip = GTK_BINARY_STRIP(widget);

    if (strip->binary == NULL)
        return FALSE;

    context = gtk_widget_get_style_context(widget);

    /* Dessin des portions de binaire */

    format = g_loaded_binary_get_format(strip->binary);
    portions = g_exe_format_get_portions(format);

    full.x = 0;
    full.y = 1;
    full.width = gtk_widget_get_allocated_width(widget);
    full.height = gtk_widget_get_allocated_height(widget) - 1;

    g_binary_portion_draw(portions, context, cr, &full);

    g_object_unref(G_OBJECT(portions));
    g_object_unref(G_OBJECT(format));

    /* Dessin de la position */

    if (strip->cursor_pos != -1)
    {
        cairo_set_line_width(cr, 1);

        gtk_style_context_get(context, GTK_STATE_FLAG_NORMAL,
                              GTK_STYLE_PROPERTY_BACKGROUND_COLOR, &color, NULL);

        cairo_set_source_rgb(cr, color->red, color->green, color->blue);

        gdk_rgba_free(color);

        cairo_move_to(cr, strip->cursor_pos, STRIP_MARKER_SIZE);
        cairo_line_to(cr, strip->cursor_pos + STRIP_MARKER_SIZE, 0);
        cairo_line_to(cr, strip->cursor_pos - STRIP_MARKER_SIZE, 0);
        cairo_line_to(cr, strip->cursor_pos, STRIP_MARKER_SIZE);
        cairo_fill(cr);

        cairo_move_to(cr, strip->cursor_pos, full.height - STRIP_MARKER_SIZE + 1);
        cairo_line_to(cr, strip->cursor_pos + STRIP_MARKER_SIZE, full.height + 1);
        cairo_line_to(cr, strip->cursor_pos - STRIP_MARKER_SIZE, full.height + 1);
        cairo_line_to(cr, strip->cursor_pos, full.height - STRIP_MARKER_SIZE + 1);
        cairo_fill(cr);

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
*                                                                             *
*  Description : Prépare l'affichage d'une astuce.                            *
*                                                                             *
*  Retour      : TRUE pour un affichage validé, FALSE sinon.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_binary_strip_query_tooltip(GtkWidget *widget, gint x, gint y, gboolean keyboard, GtkTooltip *tooltip)
{
    gboolean result;                        /* Bilan à retourner           */
    GtkBinaryStrip *strip;                  /* Autre version du composant  */
    GExeFormat *format;                     /* Format du binaire           */
    GBinPortion *portions;                  /* Couches binaires à consulter*/
    GdkRectangle area;                      /* Surface du composant        */

    if (keyboard) return FALSE;

    strip = GTK_BINARY_STRIP(widget);

    if (strip->binary != NULL)
    {
        format = g_loaded_binary_get_format(strip->binary);
        portions = g_exe_format_get_portions(format);

        area.x = 0;
        area.y = 0;
        area.width = gtk_widget_get_allocated_width(widget);
        area.height = gtk_widget_get_allocated_height(widget);

        result = query_tooltip_for_binary_portion(portions, x, y, &area, tooltip);

        g_object_unref(G_OBJECT(portions));
        g_object_unref(G_OBJECT(format));

    }

    else
        result = FALSE;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : strip  = composant GTK à mettre à jour.                      *
*                binary = nouveau contenu binaire à représenter.              *
*                                                                             *
*  Description : Attache un nouveau binaire à la barre de représentation.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_binary_strip_attach(GtkBinaryStrip *strip, GLoadedBinary *binary)
{
    GtkWidget *widget;                      /* Autre version du composant  */

    if (strip->binary != NULL)
        g_object_unref(G_OBJECT(strip->binary));

    strip->binary = binary;

    if (strip->binary != NULL)
        g_object_ref(G_OBJECT(strip->binary));

    widget = GTK_WIDGET(strip);

    gtk_widget_set_sensitive(widget, strip->binary != NULL);

    gtk_widget_queue_draw(widget);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : strip  = composant GTK à consulter.                          *
*                                                                             *
*  Description : Indique l'adresse physique et virtuelle représentée.         *
*                                                                             *
*  Retour      : Localisation, initialisée ou non.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const vmpa2t *gtk_binary_strip_get_location(const GtkBinaryStrip *strip)
{
    return &strip->cursor_addr;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : strip  = composant GTK à mettre à jour.                      *
*                binary = nouveau contenu binaire à représenter.              *
*                                                                             *
*  Description : Place le curseur dans la barre de représentation.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#if 0
void gtk_binary_strip_locate_cursor(GtkBinaryStrip *strip, vmpa_t addr, bool emit)
{
    //srip->cursor_pos = pos;

    gtk_widget_queue_draw(GTK_WIDGET(strip));

}
#endif
