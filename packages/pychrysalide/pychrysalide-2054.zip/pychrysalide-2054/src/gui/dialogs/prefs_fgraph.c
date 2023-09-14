
/* Chrysalide - Outil d'analyse de fichiers binaires
 * prefs_fgraph.c - options relatives aux graphiques de fonction
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


#include "prefs_fgraph.h"


#include <assert.h>


#include "../../core/params.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur à détruire après usage. [OUT]         *
*                                                                             *
*  Description : Met en place un panneau de paramétrage pour graphiques.      *
*                                                                             *
*  Retour      : Adresse du composant GTK prêt à emploi.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_fgraph_preferences(GtkBuilder **builder)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */

    *builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/prefs_fgraph.ui");

    result = GTK_WIDGET(gtk_builder_get_object(*builder, "panel"));

    g_object_ref(G_OBJECT(result));

    gtk_widget_unparent(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur contenant les références du dialogue. *
*                config  = configuration globale à consulter.                 *
*                                                                             *
*  Description : Charge la configuration des paramétrages pour graphiques.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_fgraph_configuration(GtkBuilder *builder, GGenConfig *config)
{
    GdkRGBA color;                          /* Couleur de lien définie     */
#ifndef NDEBUG
    bool status;                            /* Validité d'une couleur      */
#endif
    GtkColorChooser *chooser;               /* Bouton de sélection         */

#ifndef NDEBUG
    status = g_generic_config_get_value(config, MPK_LINK_DEFAULT, &color);
    assert(status);
#else
    g_generic_config_get_value(config, MPK_LINK_DEFAULT, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "def_button"));

    gtk_color_chooser_set_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_get_value(config, MPK_LINK_BRANCH_TRUE, &color);
    assert(status);
#else
    g_generic_config_get_value(config, MPK_LINK_BRANCH_TRUE, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "true_button"));

    gtk_color_chooser_set_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_get_value(config, MPK_LINK_BRANCH_FALSE, &color);
    assert(status);
#else
    g_generic_config_get_value(config, MPK_LINK_BRANCH_FALSE, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "false_button"));

    gtk_color_chooser_set_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_get_value(config, MPK_LINK_LOOP, &color);
    assert(status);
#else
    g_generic_config_get_value(config, MPK_LINK_LOOP, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "loop_button"));

    gtk_color_chooser_set_rgba(chooser, &color);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur contenant les références du dialogue. *
*                config  = configuration globale à consulter.                 *
*                                                                             *
*  Description : Sauvegarde la configuration des paramétrages pour graphiques.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void store_fgraph_configuration(GtkBuilder *builder, GGenConfig *config)
{
    GtkColorChooser *chooser;               /* Bouton de sélection         */
    GdkRGBA color;                          /* Couleur de lien définie     */
#ifndef NDEBUG
    bool status;                            /* Validité d'une couleur      */
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "def_button"));

    gtk_color_chooser_get_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_set_value(config, MPK_LINK_DEFAULT, &color);
    assert(status);
#else
    g_generic_config_set_value(config, MPK_LINK_DEFAULT, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "true_button"));

    gtk_color_chooser_get_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_set_value(config, MPK_LINK_BRANCH_TRUE, &color);
    assert(status);
#else
    g_generic_config_set_value(config, MPK_LINK_BRANCH_TRUE, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "false_button"));

    gtk_color_chooser_get_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_set_value(config, MPK_LINK_BRANCH_FALSE, &color);
    assert(status);
#else
    g_generic_config_set_value(config, MPK_LINK_BRANCH_FALSE, &color);
#endif

    chooser = GTK_COLOR_CHOOSER(gtk_builder_get_object(builder, "loop_button"));

    gtk_color_chooser_get_rgba(chooser, &color);

#ifndef NDEBUG
    status = g_generic_config_set_value(config, MPK_LINK_LOOP, &color);
    assert(status);
#else
    g_generic_config_set_value(config, MPK_LINK_LOOP, &color);
#endif

}
