
/* Chrysalide - Outil d'analyse de fichiers binaires
 * about.h - boîte de dialogue d'information sur le programme
 *
 * Copyright (C) 2015-2020 Cyrille Bagard
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


#include "about.h"


#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <gdk/gdkkeysyms.h>


#include <config.h>


#include "../../gtkext/easygtk.h"



/* Réagit à l'appui d'une touche sur la fenêtre 'A propos'. */
static gboolean close_about_window_on_escape(GtkWidget *, GdkEventKey *, gpointer);

/* Dessine un fond adapté pour la fenêtre sans toucher au thème. */
static gboolean draw_black_background(GtkWidget *, cairo_t *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre parente à surpasser.                        *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Construit la fenêtre d'informations sur le logiciel.         *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_about_dialog(GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    unsigned int revision;                  /* Numéro de révision          */
    unsigned int max;                       /* Nbre. de boucles à effectuer*/
    unsigned int i;                         /* Boucle de parcours          */
    unsigned int level;                     /* Unité la plus importante    */
    char buffer[64];                        /* Nom d'image à forger        */
    GtkImage *img;                          /* Composant d'affichage       */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/about.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    /* Numéro de révision */

    revision = REVISION;
    max = log(revision) / log(10);

    assert(max <= 6);

    for (i = 0; i <= max; i++)
    {
        snprintf(buffer, 64, "revision_%u", i);

        img = GTK_IMAGE(gtk_builder_get_object(builder, buffer));

        level = pow(10, max - i);

        snprintf(buffer, 64, "/org/chrysalide/gui/dialogs/about/revision_%u.png", revision / level);

        gtk_image_set_from_resource(img, buffer);

        revision %= level;

    }

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(close_about_window_on_escape),
                                     BUILDER_CALLBACK(draw_black_background),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = fenêtre visée par la procédure.                     *
*                event  = informations liées à l'événement.                   *
*                dummy  = donnée non utilisée ici.                            *
*                                                                             *
*  Description : Réagit à l'appui d'une touche sur la fenêtre 'A propos'.     *
*                                                                             *
*  Retour      : TRUE pour interrompre la propagation, FALSE autrement.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean close_about_window_on_escape(GtkWidget *widget, GdkEventKey *event, gpointer dummy)
{
    gboolean result;                        /* Ordre à retourner           */

    if (event->keyval == GDK_KEY_Escape)
    {
        gtk_widget_destroy(widget);
        result = TRUE;
    }
    else result = FALSE;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = fenêtre visée par la procédure.                     *
*                event  = informations liées à l'événement.                   *
*                dummy  = donnée non utilisée ici.                            *
*                                                                             *
*  Description : Dessine un fond adapté pour la fenêtre sans toucher au thème.*
*                                                                             *
*  Retour      : TRUE pour interrompre la propagation, FALSE autrement.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean draw_black_background(GtkWidget *widget, cairo_t *cr, gpointer dummy)
{
    int width;                              /* Largeur du composant        */
    int height;                             /* Hauteur du composant        */

    width = gtk_widget_get_allocated_width(widget);
    height = gtk_widget_get_allocated_height(widget);

    cairo_set_source_rgb(cr, 0.0, 0.0, 0.0);

    cairo_rectangle(cr, 0, 0, width, height);
    cairo_fill(cr);

    return FALSE;

}
