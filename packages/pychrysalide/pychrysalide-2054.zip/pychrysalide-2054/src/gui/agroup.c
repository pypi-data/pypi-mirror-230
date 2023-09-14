
/* Chrysalide - Outil d'analyse de fichiers binaires
 * agroup.h - prototypes pour l'activation et la désactivation de tous les raccourcis clavier
 *
 * Copyright (C) 2018 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "agroup.h"


#include <stdbool.h>


#include "../gtkext/easygtk.h"



/* Détermine si un élément graphique peut être actionné. */
static gboolean enable_accel_all_the_time(GtkWidget *, guint, gpointer);

/* Détermine si un élément graphique peut être actionné. */
static gboolean enable_accel_with_care(GtkWidget *, guint, gpointer);


/* Suivi des autorisations suivant la zone active. */
static bool _entry_focused = false;



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Précise l'accès aux menus avec raccourcis.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_accel_group_callbacks(GtkBuilder *builder)
{
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(enable_accel_all_the_time),
                                     BUILDER_CALLBACK(enable_accel_with_care),
                                     NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget    = composant graphique à analyser.                  *
*                signal_id = identifiant de signal.                           *
*                unused    = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Détermine si un élément graphique peut être actionné.        *
*                                                                             *
*  Retour      : TRUE si l'élément de menu est accessible.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean enable_accel_all_the_time(GtkWidget *widget, guint signal_id, gpointer unused)
{
    gboolean result;                        /* Indication à retourner      */

    result = gtk_widget_is_sensitive(widget);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget    = composant graphique à analyser.                  *
*                signal_id = identifiant de signal.                           *
*                unused    = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Détermine si un élément graphique peut être actionné.        *
*                                                                             *
*  Retour      : TRUE si l'élément de menu est accessible.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean enable_accel_with_care(GtkWidget *widget, guint signal_id, gpointer unused)
{
    gboolean result;                        /* Indication à retourner      */

    result = !_entry_focused && enable_accel_all_the_time(widget, signal_id, unused);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder     = constructeur associé à l'interface principale. *
*                widget      = composant GTK à traiter.                       *
*                accelerator = description sous forme de chaîne de caractères.*
*                                                                             *
*  Description : Ajoute un accélérateur à un composant graphique.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_accelerator_to_widget(GtkBuilder *builder, GtkWidget *widget, const char *accelerator)
{
    guint key;                              /* Touche concernée            */
    GdkModifierType mods;                   /* Eventuels modificateurs     */
    GtkAccelGroup *group;                   /* Groupe de raccourcis        */

    gtk_accelerator_parse(accelerator, &key, &mods);

    if (mods == 0)
        g_signal_connect(widget, "can-activate-accel", G_CALLBACK(enable_accel_with_care), NULL);
    else
        g_signal_connect(widget, "can-activate-accel", G_CALLBACK(enable_accel_all_the_time), NULL);

    group = GTK_ACCEL_GROUP(gtk_builder_get_object(builder, "accelgroup"));

    gtk_widget_add_accelerator(widget, "activate", group,
                               key, mods, GTK_ACCEL_VISIBLE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à l'origine de la procédure.          *
*                event  = informations liées à l'événement.                   *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Prend note d'un changement de focus sur une zone de saisie.  *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gboolean track_focus_change_in_text_area(GtkWidget *widget, GdkEventFocus *event, gpointer unused)
{
    _entry_focused = event->in;

    return FALSE;

}
