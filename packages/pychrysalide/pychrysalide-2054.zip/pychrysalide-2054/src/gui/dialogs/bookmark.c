
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmark.c - boîte de dialogue pour les sauts à une adresse donnée
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#include "bookmark.h"


#include "../../analysis/db/items/bookmark.h"
#include "../../gtkext/easygtk.h"



/* Clôture l'édition d'un signet. */
static void validate_address(GtkEntry *entry, GtkDialog *);



/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre parente à surpasser.                        *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Construit la fenêtre de création de signet.                  *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_bookmark_dialog(GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/bookmark.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(validate_address),
                                     NULL);

    gtk_builder_connect_signals(builder, result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry  = composant GTK concerné par la procédure.            *
*                dialog = boîte de dialogue à valider.                        *
*                                                                             *
*  Description : Clôture l'édition d'un signet.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void validate_address(GtkEntry *entry, GtkDialog *dialog)
{
    gtk_dialog_response(dialog, GTK_RESPONSE_OK);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = espace de référencement global.                    *
*                addr    = localisation du point à consigner.                 *
*                                                                             *
*  Description : Fournit le signet conçu via la saisie de l'utilisateur.      *
*                                                                             *
*  Retour      : Adresse reccueillie par la boîte de dialogue.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbItem *get_item_from_bookmark_dialog(GtkBuilder *builder, const vmpa2t *addr)
{
    GDbItem *result;                        /* Signet nouveau à retourner  */
    GtkEntry *entry;                        /* Zone de saisie principale   */
    const gchar *text;                      /* Adresse en version texte    */

    /* Récupération du commentaire éventuel */

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "comment"));

    text = gtk_entry_get_text(entry);

    /* Mise en place du signet défini */

    if (strlen(text) > 0)
        result = G_DB_ITEM(g_db_bookmark_new(addr, text));
    else
        result = G_DB_ITEM(g_db_bookmark_new(addr, NULL));

    return result;

}
