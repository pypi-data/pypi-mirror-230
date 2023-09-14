
/* Chrysalide - Outil d'analyse de fichiers binaires
 * identity.c - (re)définition de l'identité de l'utilisateur
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "identity.h"


#include <malloc.h>
#include <string.h>


#include <i18n.h>


#include "../../analysis/db/auth.h"
#include "../../analysis/db/certs.h"
#include "../../common/extstr.h"
#include "../../core/logs.h"
#include "../../gtkext/easygtk.h"



/* Applique la nouvelle définition d'identité. */
static void update_identity(GtkButton *, GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre principale de l'éditeur.                    *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Propose une édition d'informations concernant l'utilisateur. *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_identity_dialog(GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    char *username;                         /* Nom par défaut              */
    GtkEntry *entry;                        /* Zone de saisie à initialiser*/
    char *filename;                         /* Fichier devant être présent */
    x509_entries identity;                  /* Eléments identitaires       */
    bool status;                            /* Bilan d'un chargement       */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/identity.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    username = get_default_username();

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "cn"));
    gtk_entry_set_placeholder_text(entry, username);

    free(username);

    /* Mise à jour de l'interface */

    filename = get_db_working_directory("clients", NULL, NULL, NULL);
    filename = stradd(filename, "client-csr.pem");

    status = load_identity_from_request(filename, &identity);

    free(filename);

    if (status)
    {
        if (identity.country != NULL)
        {
            entry = GTK_ENTRY(gtk_builder_get_object(builder, "c"));
            gtk_entry_set_text(entry, identity.country);
        }

        if (identity.state != NULL)
        {
            entry = GTK_ENTRY(gtk_builder_get_object(builder, "st"));
            gtk_entry_set_text(entry, identity.state);
        }

        if (identity.locality != NULL)
        {
            entry = GTK_ENTRY(gtk_builder_get_object(builder, "l"));
            gtk_entry_set_text(entry, identity.locality);
        }

        if (identity.organisation != NULL)
        {
            entry = GTK_ENTRY(gtk_builder_get_object(builder, "o"));
            gtk_entry_set_text(entry, identity.organisation);
        }

        if (identity.organisational_unit != NULL)
        {
            entry = GTK_ENTRY(gtk_builder_get_object(builder, "ou"));
            gtk_entry_set_text(entry, identity.organisational_unit);
        }

        if (identity.common_name != NULL)
        {
            entry = GTK_ENTRY(gtk_builder_get_object(builder, "cn"));
            gtk_entry_set_text(entry, identity.common_name);

            gtk_editable_select_region(GTK_EDITABLE(entry), 0, -1);

        }

        free_x509_entries(&identity);

    }

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(update_identity),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Applique la nouvelle définition d'identité.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_identity(GtkButton *button, GtkBuilder *builder)
{
    GtkEntry *entry;                        /* Zone de saisie à consulter  */
    const gchar *data;                      /* Données internes à GTK      */
    x509_entries identity;                  /* Nouvelle identité à pousser */
    bool status;                            /* Bilan de la mise à jour     */

    /* Récupération des éléments */

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "c"));
    data = gtk_entry_get_text(entry);

    identity.country = (strlen(data) > 0 ? strdup(data) : NULL);

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "st"));
    data = gtk_entry_get_text(entry);

    identity.state = (strlen(data) > 0 ? strdup(data) : NULL);

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "l"));
    data = gtk_entry_get_text(entry);

    identity.locality = (strlen(data) > 0 ? strdup(data) : NULL);

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "o"));
    data = gtk_entry_get_text(entry);

    identity.organisation = (strlen(data) > 0 ? strdup(data) : NULL);

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "ou"));
    data = gtk_entry_get_text(entry);

    identity.organisational_unit = (strlen(data) > 0 ? strdup(data) : NULL);

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "cn"));
    data = gtk_entry_get_text(entry);

    identity.common_name = (strlen(data) > 0 ? strdup(data) : NULL);

    /* Application de la nouvelle définition */

    status = false;//register_standalone_certs(&entries);

    free_x509_entries(&identity);

    if (status)
        log_simple_message(LMT_INFO, _("New identity has been loaded with success!"));
    else
        log_simple_message(LMT_ERROR, _("Failure while reloading the new identity..."));

}
