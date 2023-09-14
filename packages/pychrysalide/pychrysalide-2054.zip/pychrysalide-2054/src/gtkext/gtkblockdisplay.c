
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkblockdisplay.c - affichage d'un fragment de code d'assemblage
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


#include "gtkblockdisplay.h"


#include "gtkbufferdisplay-int.h"
#include "../arch/instruction.h"
#include "../arch/operand.h"
#include "../analysis/loaded.h"
#include "../core/columns.h"
#include "../glibext/gbinarycursor.h"



/* Composant d'affichage de bloc d'assembleur (instance) */
struct _GtkBlockDisplay
{
    GtkBufferDisplay parent;                /* A laisser en premier        */

};

/* Composant d'affichage de code d'assembleur (classe) */
struct _GtkBlockDisplayClass
{
    GtkBufferDisplayClass parent;           /* A laisser en premier        */

    /* Signaux */

    void (* highlight_changed) (GtkBlockDisplay *);

};


/* Procède à l'initialisation des afficheurs de bloc assembleur. */
static void gtk_block_display_class_init(GtkBlockDisplayClass *);

/* Procède à l'initialisation de l'afficheur de bloc assembleur. */
static void gtk_block_display_init(GtkBlockDisplay *);

/* Supprime toutes les références externes. */
static void gtk_block_display_dispose(GtkBlockDisplay *);

/* Procède à la libération totale de la mémoire. */
static void gtk_block_display_finalize(GtkBlockDisplay *);

/* Assure la gestion des clics de souris sur le composant. */
static gboolean gtk_block_display_button_press(GtkWidget *, GdkEventButton *);

/* Prépare l'affichage d'une astuce. */
static gboolean gtk_block_display_query_tooltip(GtkWidget *, gint, gint, gboolean, GtkTooltip *);

/* Redessine l'affichage suite à un changement visuel. */
static gboolean gtk_block_display_need_redraw(GtkBlockDisplay *, GBufferView *);

/* Réagit à un déplacement de curseur. */
static bool gtk_block_display_notify_caret_relocation(GtkBlockDisplay *, const GdkRectangle *);



/* Détermine le type du composant d'affichage de bloc en langage d'assemblage. */
G_DEFINE_TYPE(GtkBlockDisplay, gtk_block_display, GTK_TYPE_BUFFER_DISPLAY)


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Procède à l'initialisation des afficheurs de bloc assembleur.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_block_display_class_init(GtkBlockDisplayClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GtkWidgetClass *widget_class;           /* Classe version Widget       */
    GtkBufferDisplayClass *buffer_class;    /* Classe supérieure           */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_block_display_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_block_display_finalize;

    widget_class = GTK_WIDGET_CLASS(class);

    widget_class->button_press_event = gtk_block_display_button_press;
    widget_class->query_tooltip = gtk_block_display_query_tooltip;

    buffer_class = GTK_BUFFER_DISPLAY_CLASS(class);

    buffer_class->notify_caret = (notify_caret_relocation_fc)gtk_block_display_notify_caret_relocation;

    /* Signaux */

    g_signal_new("highlight-changed",
                 GTK_TYPE_BLOCK_DISPLAY,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkBlockDisplayClass, highlight_changed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à initialiser.                       *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur de bloc assembleur.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_block_display_init(GtkBlockDisplay *display)
{
    GObject *object;                        /* Autre version de l'instance */

    object = G_OBJECT(display);

    g_object_set(object, "has-tooltip", TRUE, NULL);

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

static void gtk_block_display_dispose(GtkBlockDisplay *display)
{
    GBufferView *view;                      /* Vue sur du texte            */

    /**
     * Même si à priori, la vue est propre au composant, on coupe le signal
     * afin qu'une émission d'une instance de vue toujours active ne renvoie pas
     * en paramètre un composant d'affichage libéré.
     */

    view = GTK_BUFFER_DISPLAY(display)->view;

    if (view != NULL)
        g_signal_handlers_disconnect_by_func(G_OBJECT(view),
                                             G_CALLBACK(gtk_block_display_need_redraw),
                                             display);

    G_OBJECT_CLASS(gtk_block_display_parent_class)->dispose(G_OBJECT(display));

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

static void gtk_block_display_finalize(GtkBlockDisplay *display)
{
    G_OBJECT_CLASS(gtk_block_display_parent_class)->finalize(G_OBJECT(display));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = représentation à afficher dans le composant.          *
*                                                                             *
*  Description : Crée un nouveau composant pour l'affichage de bloc en ASM.   *
*                                                                             *
*  Retour      : Composant GTK créé.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_block_display_new(GBufferView *view)
{
    GtkBlockDisplay *result;                /* Composant à retourner       */

    result = g_object_new(GTK_TYPE_BLOCK_DISPLAY, NULL);

    GTK_BUFFER_DISPLAY(result)->view = view;

    g_signal_connect_swapped(G_OBJECT(view), "need-redraw",
                             G_CALLBACK(gtk_block_display_need_redraw), result);

    return GTK_WIDGET(result);

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

static gboolean gtk_block_display_button_press(GtkWidget *widget, GdkEventButton *event)
{
    GtkBlockDisplay *display;               /* Autre version du composant  */
    gint real_x;                            /* Abscisse absolue réelle     */
    gint real_y;                            /* Ordonnée absolue réelle     */
    GBufferView *view;                      /* Vue du tampon représenté    */
    bool changed;                           /* Suivi des changements       */

    GTK_WIDGET_CLASS(gtk_block_display_parent_class)->button_press_event(widget, event);

    display = GTK_BLOCK_DISPLAY(widget);

    if (event->type == GDK_2BUTTON_PRESS)
    {
        real_x = event->x;
        real_y = event->y;

        gtk_display_panel_compute_real_coord(GTK_DISPLAY_PANEL(display), &real_x, &real_y);

        view = gtk_buffer_display_get_view(GTK_BUFFER_DISPLAY(display));

        changed = g_buffer_view_highlight_segments(view, real_x, real_y, GTK_DISPLAY_PANEL(display)->options);

        g_object_unref(G_OBJECT(view));

        if (changed)
            g_signal_emit_by_name(display, "highlight-changed");

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

static gboolean gtk_block_display_query_tooltip(GtkWidget *widget, gint x, gint y, gboolean keyboard, GtkTooltip *tooltip)
{
    gboolean result;                        /* Bilan à retourner           */
    GtkBlockDisplay *display;               /* Autre version du composant  */
    GtkDisplayPanel *panel;                 /* Version racine du composant */
    gint real_x;                            /* Abscisse absolue réelle     */
    gint real_y;                            /* Ordonnée absolue réelle     */
    GObject *creator;                       /* Origine du segment pointé   */
    char *info;                             /* Information à faire paraître*/

    if (keyboard) return FALSE;

    result = FALSE;

    display = GTK_BLOCK_DISPLAY(widget);
    panel = GTK_DISPLAY_PANEL(display);

    real_x = x;
    real_y = y;
    gtk_display_panel_compute_real_coord(panel, &real_x, &real_y);

    creator = g_buffer_view_find_creator(GTK_BUFFER_DISPLAY(display)->view, real_x, real_y, panel->options);

    if (creator != NULL)
    {
        if (G_IS_ARCH_INSTRUCTION(creator))
            info = g_arch_instruction_build_tooltip(G_ARCH_INSTRUCTION(creator));

        else if (G_IS_ARCH_OPERAND(creator))
            info = g_arch_operand_build_tooltip(G_ARCH_OPERAND(creator), panel->binary);

        else
            info = NULL;

        if (info != NULL)
        {
            gtk_tooltip_set_markup(tooltip, info);
            free(info);

            result = TRUE;

        }

        g_object_unref(creator);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK d'affichage.                         *
*                view    = composant GLib interne.                            *
*                                                                             *
*  Description : Redessine l'affichage suite à un changement visuel.          *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_block_display_need_redraw(GtkBlockDisplay *display, GBufferView *view)
{
    GtkWidget *widget;                      /* Autre version du composant  */

    gtk_widget_queue_draw(GTK_WIDGET(display));

    /**
     * Pour une raison non comprise, le redessin n'est pris en compte que
     * si le parent est concerné également...
     */

    widget = gtk_widget_get_parent(GTK_WIDGET(display));

    if (GTK_IS_SCROLLED_WINDOW(widget))
        gtk_widget_queue_draw(widget);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK à manipuler.                         *
*                area    = emplacement pour le dessin d'un curseur.           *
*                                                                             *
*  Description : Réagit à un déplacement de curseur.                          *
*                                                                             *
*  Retour      : true si un changement a été opéré.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool gtk_block_display_notify_caret_relocation(GtkBlockDisplay *display, const GdkRectangle *area)
{
    bool result;                            /* Bilan à retourner           */
    GBufferView *view;                      /* Vue du tampon représenté    */

    view = gtk_buffer_display_get_view(GTK_BUFFER_DISPLAY(display));

    result = g_buffer_view_highlight_segments(view, area->x, area->y, GTK_DISPLAY_PANEL(display)->options);

    g_object_unref(G_OBJECT(view));

    if (result)
        g_signal_emit_by_name(display, "highlight-changed");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : display = composant GTK d'affichage.                         *
*                index   = indice de type de vue effectif.                    *
*                                                                             *
*  Description : Force un type de vue pour les options de rendu.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_block_display_override_view_index(GtkBlockDisplay *display, unsigned int index)
{
    GtkDisplayPanel *panel;                 /* Version de plus haut niveau */
    GBufferCache *cache;                    /* Tampon de données affiché   */
    GWidthTracker *tracker;                 /* Gestionnaire de largeurs    */

    panel = GTK_DISPLAY_PANEL(display);

    panel->view_index = index;
    panel->options = g_loaded_content_get_display_options(G_LOADED_CONTENT(panel->binary), index);

    cache = g_buffer_view_get_cache(GTK_BUFFER_DISPLAY(display)->view);

    tracker = g_buffer_cache_get_width_tracker(cache);
    g_width_tracker_set_column_min_width(tracker, DLC_ASSEMBLY_LABEL, 0);
    g_object_unref(G_OBJECT(tracker));

    g_object_unref(G_OBJECT(cache));

    gtk_buffer_display_add_block_bar(GTK_BUFFER_DISPLAY(display));

}
