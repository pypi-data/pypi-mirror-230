
/* Chrysalide - Outil d'analyse de fichiers binaires
 * prefs_labels.c - paramètres des étiquettes colorées
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "prefs_labels.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur à détruire après usage. [OUT]         *
*                                                                             *
*  Description : Met en place un panneau de paramétrage d'étiquettes colorées.*
*                                                                             *
*  Retour      : Adresse du composant GTK prêt à emploi.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_labels_preferences(GtkBuilder **builder)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */

    *builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/prefs_labels.ui");

    result = GTK_WIDGET(gtk_builder_get_object(*builder, "panel"));

    g_object_ref(G_OBJECT(result));

    gtk_widget_unparent(result);

    /* Connexion des signaux */

    /*
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(update_preferences),
                                     NULL);
    */

    gtk_builder_connect_signals(*builder, *builder);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur contenant les références du dialogue. *
*                config  = configuration globale à consulter.                 *
*                                                                             *
*  Description : Charge la configuration des paramétrages pour étiquettes.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_labels_configuration(GtkBuilder *builder, GGenConfig *config)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur contenant les références du dialogue. *
*                config  = configuration globale à consulter.                 *
*                                                                             *
*  Description : Sauvegarde la configuration des paramétrages pour étiquettes.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void store_labels_configuration(GtkBuilder *builder, GGenConfig *config)
{

}
