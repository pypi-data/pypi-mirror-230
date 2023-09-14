
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.c - définition des modes d'enregistrement pour binaires
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


#include "storage.h"


#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>


#include "../../gtkext/easygtk.h"



/* Réagit à un changement dans le choix du type de serveur. */
static void on_server_use_toggled(GtkToggleButton *, GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire chargé en mémoire à traiter.                *
*                parent = fenêtre principale de l'éditeur.                    *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Propose une définition des propriétés d'enregistrement.      *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_storage_dialog(GLoadedBinary *binary, GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkToggleButton *use_remote;            /* Choix du serveur distant    */
    const char *host;                       /* Serveur distant à contacter */
    const char *port;                       /* Port d'écoute du serveur    */
    GObject *widget;                        /* Composant à mettre à jour   */
    GtkListStore *store;                    /* Modèle de gestion           */
    GDbCollection **collections;            /* Ensemble de collections     */
    size_t count;                           /* Taille de cet ensemble      */
    size_t i;                               /* Boucle de parcours          */
    uint32_t feature;                       /* Type d'éléments gérés       */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/storage.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    /* Mise à jour de l'interface */

    use_remote = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "use_remote"));

    if (g_loaded_binary_use_remote_storage(binary))
        gtk_toggle_button_set_active(use_remote, TRUE);
    else
        gtk_toggle_button_set_active(use_remote, FALSE);

    g_loaded_binary_get_remote_server(binary, &host, &port);

    widget = gtk_builder_get_object(builder, "server");
    gtk_entry_set_text(GTK_ENTRY(widget), host);

    widget = gtk_builder_get_object(builder, "port");
    gtk_spin_button_set_value(GTK_SPIN_BUTTON(widget), atoi(port));

    on_server_use_toggled(use_remote, builder);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_server_use_toggled),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à un changement dans le choix du type de serveur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_server_use_toggled(GtkToggleButton *button, GtkBuilder *builder)
{
    gboolean active;                        /* Etat du choix du distant    */
    GtkWidget *widget;                      /* Composant à modifier        */

    active = gtk_toggle_button_get_active(button);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "server_label"));
    gtk_widget_set_sensitive(widget, active);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "server"));
    gtk_widget_set_sensitive(widget, active);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "port_label"));
    gtk_widget_set_sensitive(widget, active);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "port"));
    gtk_widget_set_sensitive(widget, active);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = espace de référencement global.                    *
*                binary  = binaire chargé en mémoire à traiter.               *
*                                                                             *
*  Description : Applique les paramètres d'enregistrement pour un binaire.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_binary_storage(GtkBuilder *builder, GLoadedBinary *binary)
{
    GObject *widget;                        /* Composant à mettre à jour   */
    const gchar *host;                      /* Serveur distant à contacter */
    gint raw_port;                          /* Port d'écoute du serveur    */
    char *port;                             /* Port d'écoute du serveur    */
    GtkToggleButton *use_remote;            /* Choix du serveur distant    */
    gboolean active;                        /* Etat du choix du distant    */
    GtkTreeModel *model;                    /* Modèle de gestion utilisé   */
    GtkTreeIter iter;                       /* Itérateur de consultation   */
    gboolean valid;                         /* Validité de l'itérateur     */
    GDbCollection *collec;                  /* Collection à traiter        */
    gboolean local;                         /* Conservation locale ?       */
    uint32_t feature;                       /* Type d'éléments gérés       */

    /* Infos de connexions à distance */

    widget = gtk_builder_get_object(builder, "server");
    host = gtk_entry_get_text(GTK_ENTRY(widget));

    widget = gtk_builder_get_object(builder, "port");
    raw_port = gtk_spin_button_get_value_as_int(GTK_SPIN_BUTTON(widget));

    asprintf(&port, "%d", raw_port);

    g_loaded_binary_set_remote_server(binary, host, port);

    free(port);

    /* Choix final du serveur */

    use_remote = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "use_remote"));

    active = gtk_toggle_button_get_active(use_remote);

    g_loaded_binary_set_remote_storage_usage(binary, active);

}
