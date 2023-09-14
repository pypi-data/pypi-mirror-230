
/* Chrysalide - Outil d'analyse de fichiers binaires
 * easygtk.c - mise en place rapide de composants GTK
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "easygtk.h"


#include <assert.h>
#include <stdint.h>


#include "support.h"



/* Termine la construction d'un composant 'GtkButton'. */
static void _finish_button_with_img(GtkWidget *, GObject *, const char *, GtkWidget *, const char *);

/* Encadre certains raccourcis actionnés sur un menu. */
static gboolean handle_escape_on_menu(GtkWidget *, GdkEventKey *, GtkMenuItem *);



/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique visé par la procédure.          *
*                pt     = espace imposé à la zone supérieure.                 *
*                pb     = espace imposé à la zone inférieure.                 *
*                pl     = espace imposé à la zone gauche.                     *
*                pr     = espace imposé à la zone droite.                     *
*                                                                             *
*  Description : Définit des bordures extérieures à appliquer à un composant. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void qck_set_margins(GtkWidget *widget, guint pt, guint pb, guint pl, guint pr)
{
    gtk_widget_set_margin_top(widget, pt);
    gtk_widget_set_margin_bottom(widget, pb);

    gtk_widget_set_margin_start(widget, pl);
    gtk_widget_set_margin_end(widget, pr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caption = contenu de l'étiqutte à placer.                    *
*                content = composant en place à poser sur le conteneur.       *
*                pt      = espace imposé à la zone supérieure.                *
*                pb      = espace imposé à la zone inférieure.                *
*                pl      = espace imposé à la zone gauche.                    *
*                pr      = espace imposé à la zone droite.                    *
*                                                                             *
*  Description : Met en place une frame.                                      *
*                                                                             *
*  Retour      : Composant 'GtkWidget' ici créé.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_frame(const char *caption, GtkWidget *content, guint pt, guint pb, guint pl, guint pr)
{
    GtkWidget *result;                      /* Instance à renvoyer         */
    GtkWidget *label;                       /* Etiquette à utiliser        */

    result = gtk_frame_new(NULL);
    gtk_widget_show(result);

    gtk_frame_set_shadow_type(GTK_FRAME(result), GTK_SHADOW_NONE);

    label = qck_create_label(NULL, NULL, caption);
    gtk_frame_set_label_widget(GTK_FRAME(result), label);
    gtk_label_set_use_markup(GTK_LABEL(label), TRUE);

    qck_set_margins(content, pt, pb, pl, pr);
    gtk_container_add(GTK_CONTAINER(result), content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object = espace dédié à l'inscription de références.         *
*                name   = nom à donner au nouveau composant.                  *
*                                                                             *
*  Description : Met en place un support avec défilement automatique.         *
*                                                                             *
*  Retour      : Composant 'GtkWidget' ici créé.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_scrolled_window(GObject *object, const char *name)
{
    GtkWidget *result;                      /* Instance à renvoyer         */

    result = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(result),
                                   GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                caption = intitulé apparaissant sur le composant.            *
*                                                                             *
*  Description : Crée un composant 'GtkLabel'.                                *
*                                                                             *
*  Retour      : Champ d'indication mis en place.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_label(GObject *object, const char *name, const char *caption)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_label_new(caption);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);
    gtk_widget_set_halign(result, GTK_ALIGN_START);
    gtk_widget_set_valign(result, GTK_ALIGN_CENTER);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object = espace dédié à l'inscription de références.         *
*                name   = nom à donner au nouveau composant.                  *
*                text   = éventuel contenu initial du champ de saisie.        *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkEntry'.                  *
*                                                                             *
*  Retour      : Champ de saisie mis en place.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_entry(GObject *object, const char *name, const char *text)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_entry_new();

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

	if (text != NULL)
	    gtk_entry_set_text(GTK_ENTRY(result), text);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                caption = intitulé du bouton à créer.                        *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkButton'.                 *
*                                                                             *
*  Retour      : Simple bouton mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_button(GObject *object, const char *name, const char *caption, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_button_new_with_mnemonic(caption);
    gtk_widget_set_can_default(result, TRUE);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "clicked", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant graphique dont la définition est à finir.*
*                object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                picture = éventuelle image sous forme de composant GTK.      *
*                label   = contenu de l'étiquette éventuelle associée.        *
*                                                                             *
*  Description : Termine la construction d'un composant 'GtkButton'.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _finish_button_with_img(GtkWidget *button, GObject *object, const char *name, GtkWidget *picture, const char *label)
{
    GtkWidget *caption;                     /* Etiquette à coller          */
    GtkWidget *hbox;                        /* Séparation horizontale      */

    /* Création des éléments internes (2/2) */

    if (label != NULL)
    {
        caption = gtk_label_new_with_mnemonic(label);
        gtk_widget_show(caption);
    }

    /* Mise en place */

    if (picture != NULL && label != NULL)
    {
        hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 2);
        gtk_widget_show(hbox);
        gtk_container_add(GTK_CONTAINER(button), hbox);

        gtk_box_pack_start(GTK_BOX(hbox), picture, FALSE, FALSE, 0);
        gtk_box_pack_start(GTK_BOX(hbox), caption, FALSE, FALSE, 0);

    }

    else if (picture != NULL)
        gtk_container_add(GTK_CONTAINER(button), picture);

    else if (label != NULL)
        gtk_container_add(GTK_CONTAINER(button), caption);

    else
        assert(0);

    /* Interactions GTK... */

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(button));
        g_object_set_data_full(object, name, button, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(button);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                image   = nom de l'image stockée dans GTK.                   *
*                size    = taille de l'image éventuelle à faire figurer.      *
*                label   = contenu de l'étiquette éventuelle associée.        *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkButton'.                 *
*                                                                             *
*  Retour      : Simple bouton mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_button_with_named_img(GObject *object, const char *name, const char *image, GtkIconSize size, const char *label, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */
    GtkWidget *picture;                     /* Image de représentation     */

    result = gtk_button_new();
    gtk_widget_set_can_default(result, TRUE);

    /* Création des éléments internes (1/2) */

    if (image != NULL)
    {
        picture = gtk_image_new_from_icon_name(image, size);
        gtk_widget_show(picture);
    }
    else
        picture = NULL;

    _finish_button_with_img(result, object, name, picture, label);

    if (handler != NULL)
        g_signal_connect(result, "clicked", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                image   = nom de l'image stockée dans GTK.                   *
*                size    = taille de l'image éventuelle à faire figurer.      *
*                label   = contenu de l'étiquette éventuelle associée.        *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkCheckButton'.            *
*                                                                             *
*  Retour      : Simple bouton mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_toggle_button_with_named_img(GObject *object, const char *name, const char *image, GtkIconSize size, const char *label, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */
    GtkWidget *picture;                     /* Image de représentation     */

    result = gtk_toggle_button_new();
    gtk_widget_set_can_default(result, TRUE);

    /* Création des éléments internes (1/2) */

    if (image != NULL)
    {
        picture = gtk_image_new_from_icon_name(image, size);
        gtk_widget_show(picture);
    }
    else
        picture = NULL;

    _finish_button_with_img(result, object, name, picture, label);

    if (handler != NULL)
        g_signal_connect(result, "toggled", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                caption = désignation apparaîssant sur le corps de l'objet.  *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkCheckButton'.            *
*                                                                             *
*  Retour      : Composant mis en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_check_button(GObject *object, const char *name, const char *caption, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

	result = gtk_check_button_new_with_label(caption);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "toggled", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                caption = désignation apparaîssant sur le corps de l'objet.  *
*                member  = membre de la liste des autres boutons.             *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkRadioButton'.            *
*                                                                             *
*  Retour      : Composant mis en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_radio_button(GObject *object, const char *name, const char *caption, GtkRadioButton *member, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

	result = gtk_radio_button_new_with_label_from_widget(member, caption);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "toggled", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkComboBox'.               *
*                                                                             *
*  Retour      : Composant mis en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_combobox(GObject *object, const char *name, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_combo_box_text_new();

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "changed", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkComboBox'.               *
*                                                                             *
*  Retour      : Composant mis en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_combobox_with_entry(GObject *object, const char *name, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_combo_box_text_new_with_entry();

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "changed", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menu  = composant actif pour la réception des touches.       *
*                event = informations liées à l'événement.                    *
*                item  = menu parent à manipuler au besoin.                   *
*                                                                             *
*  Description : Encadre certains raccourcis actionnés sur un menu.           *
*                                                                             *
*  Retour      : FALSE afin de poursuivre la propagation de l'événement.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean handle_escape_on_menu(GtkWidget *menu, GdkEventKey *event, GtkMenuItem *item)
{
    if (event->keyval == GDK_KEY_Escape)
    {
        gtk_widget_hide(menu);
        gtk_menu_item_deselect(item);
    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de menu devant recevoir un sous-menu.         *
*                                                                             *
*  Description : Met en place un support de menu 'GtkMenu'.                   *
*                                                                             *
*  Retour      : Réceptacle pour sous-éléments de menu.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_menu(GtkMenuItem *item)
{
    GtkWidget *result;                      /* Composant à retourner       */

    result = gtk_menu_new();

    if (item != NULL)
    {
        gtk_menu_item_set_submenu(item, result);

        g_signal_connect(result, "key-press-event", G_CALLBACK(handle_escape_on_menu), item);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                caption = intitulé du menu à créer.                          *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkMenuItem'.               *
*                                                                             *
*  Retour      : Simple élément de menu mis en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_menu_item(GObject *object, const char *name, const char *caption, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_menu_item_new_with_mnemonic(caption);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "activate", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                caption = intitulé du menu à créer.                          *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkCheckMenuItem'.          *
*                                                                             *
*  Retour      : Simple élément de menu mis en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_check_menu_item(GObject *object, const char *name, const char *caption, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_check_menu_item_new_with_mnemonic(caption);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "toggled", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = espace dédié à l'inscription de références.        *
*                name    = nom à donner au nouveau composant.                 *
*                rgroup  = groupe d'apparatenance pour les radios.            *
*                caption = intitulé du menu à créer.                          *
*                handler = éventuelle fonction de sélection associée.         *
*                data    = données à transmettre avec l'événement si besoin.  *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkRadioMenuItem'.          *
*                                                                             *
*  Retour      : Simple élément de menu mis en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_radio_menu_item(GObject *object, const char *name, GSList *rgroup, const char *caption, GCallback handler, gpointer data)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_radio_menu_item_new_with_mnemonic(rgroup, caption);

    if (G_IS_OBJECT(object) && name != NULL)
    {
        g_object_ref(G_OBJECT(result));
        g_object_set_data_full(object, name, result, (GDestroyNotify)g_object_unref);
    }

    gtk_widget_show(result);

    if (handler != NULL)
        g_signal_connect(result, "toggled", handler, data);

	return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée et enregistre un composant 'GtkSeparatorMenuItem'.      *
*                                                                             *
*  Retour      : Simple élément de menu mis en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *qck_create_menu_separator(void)
{
    GtkWidget *result;                      /* Résultat à renvoyer         */

    result = gtk_separator_menu_item_new();
    gtk_widget_show(result);

    return result;

}






/******************************************************************************
*                                                                             *
*  Paramètres  : class      = classe de style à appliquer.                    *
*                background = indique la nature de la couleur à relever.      *
*                color      = couleur associée au style indiqué. [OUT]        *
*                                                                             *
*  Description : Identifie la couleur de base associée à un style GTK.        *
*                                                                             *
*  Retour      : Bilan présumé de l'opération.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_color_from_style(const char *class, bool background, GdkRGBA *color)
{
    bool result;                            /* Bilan à retourner           */
    GtkWidget *area;                        /* Composant pour le contexte  */
    GtkStyleContext *context;               /* Contexte de style GTK       */
    cairo_surface_t *surface;               /* Surface de dessin temporaire*/
    cairo_t *cr;                            /* Pinceau pour le dessin      */
    uint32_t *pixel;                        /* Valeurs pour un pixel choisi*/
    int a;                                  /* Valeur du canal alpha       */
    int r;                                  /* Valeur du canal rouge       */
    int g;                                  /* Valeur du canal vert        */
    int b;                                  /* Valeur du canal bleu        */

    result = false;

    /* Mise en place de l'environnement */

    area = gtk_drawing_area_new();
    g_object_ref_sink(G_OBJECT(area));

    context = gtk_widget_get_style_context (area);

    surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, 20, 20);

    if (cairo_surface_status(surface) != CAIRO_STATUS_SUCCESS)
        goto empty_surface;

    cr = cairo_create(surface);

    if (cairo_status(cr) != CAIRO_STATUS_SUCCESS)
        goto bad_cairo;

    /* Dessin */

    gtk_style_context_add_class(context, class);

    if (background)
        gtk_render_background(context, cr, 0, 0, 20, 20);
    else
        gtk_render_line(context, cr, -0.5, -0.5, 19.5, 19.5);

    cairo_surface_flush(surface);

    /* Récupération du pixel (0 ; 0) */

    pixel = (uint32_t *)cairo_image_surface_get_data(surface);

    /* Récupération des valeurs de couleur */

    a = (*pixel & 0xff000000) >> 24;
    r = (*pixel & 0x00ff0000) >> 16;
    g = (*pixel & 0x0000ff00) >> 8;
    b = (*pixel & 0x000000ff);

	if (a == 0)
    {
        r = 0;
        g = 0;
        b = 0;

    }
    else
    {
        /**
         * Utilisation de la méthode employée dans la fonction
         * _cairo_image_analyze_color() de cairo-image-surface.c.
         *
         * La documentation pour CAIRO_FORMAT_ARGB32 précise en effet :
         *
         *   """
         *   each pixel is a 32-bit quantity, with alpha in the upper 8 bits,
         *   then red, then green, then blue. The 32-bit quantities are
         *   native-endian. Pre-multiplied alpha is used. (That is, 50%
         *   transparent red is 0x80800000, not 0x80ff0000.)
         *   """
         */

        r = (r * 255 + a / 2) / a;
        g = (g * 255 + a / 2) / a;
        b = (b * 255 + a / 2) / a;

    }

    color->alpha = (1.0 * a) / 0xff;
    color->red = (1.0 * r) / 0xff;
    color->green = (1.0 * g) / 0xff;
    color->blue = (1.0 * b) / 0xff;

    result = true;

    /* Renvoi des conclusions */

 bad_cairo:

    cairo_destroy(cr);

 empty_surface:

    cairo_surface_destroy(surface);

    g_object_unref(G_OBJECT(area));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : container = composant GTK contenant d'autres composants.     *
*                child     = composant GTK à retrouver.                       *
*                                                                             *
*  Description : Détermine l'indice d'un composant dans un conteneur GTK.     *
*                                                                             *
*  Retour      : Indice du composant dans le conteneur ou -1 si non trouvé.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint find_contained_child_index(GtkContainer *container, GtkWidget *child)
{
    gint result;                            /* Indice à retourner          */
    GList *list;                            /* Liste de composants contenus*/
    gint counter;                           /* Décompte progressif         */
    GList *iter;                            /* Boucle de parcours          */

    result = -1;

    list = gtk_container_get_children(container);

    counter = 0;

    for (iter = g_list_first(list); iter != NULL; iter = g_list_next(iter))
    {
        if (iter->data == child)
        {
            result = counter;
            break;
        }

        counter++;

    }

    g_list_free(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : container = composant GTK contenant d'autres composants.     *
*                n         = indice du composant à retrouver.                 *
*                                                                             *
*  Description : Récupère le nième composant d'un conteneur GTK.              *
*                                                                             *
*  Retour      : Composant à la position donnée ou NULL en cas d'absence.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *get_nth_contained_child(GtkContainer *container, guint n)
{
    GtkWidget *result;                      /* Résultat à retourner        */
    GList *list;                            /* Liste de composants contenus*/

    result = NULL;

    list = gtk_container_get_children(container);

    result = g_list_nth_data(list, n);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    g_list_free(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent   = fenêtre parente pour la modalité d'affichage.     *
*                title    = titre de la boîte de dialogue.                    *
*                question = teneur de la question posée.                      *
*                                                                             *
*  Description : Affiche une boîte de dialogue offrant un choix "Oui/Non".    *
*                                                                             *
*  Retour      : Identifiant de la réponse choisie.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint qck_show_question(GtkWindow *parent, const char *title, const char *question)
{
    gint result;                            /* Choix arrêté à renvoyer     */
    GtkWidget *dialog;                      /* Boîte de dialogue affichée  */

    dialog = gtk_message_dialog_new(parent,
                                    GTK_DIALOG_DESTROY_WITH_PARENT,
                                    GTK_MESSAGE_QUESTION,
                                    GTK_BUTTONS_YES_NO,
                                    "%s", question);

    gtk_window_set_title(GTK_WINDOW(dialog), title);

    result = gtk_dialog_run(GTK_DIALOG(dialog));

    gtk_widget_destroy(dialog);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : treeview = représentation graphique d'une liste à traiter.   *
*                model    = gestionnaire des données de la liste.             *
*                iter     = point à considérer pour l'opération.              *
*                                                                             *
*  Description : Fait défiler une liste jusqu'à un point donné.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void scroll_to_treeview_iter(GtkTreeView *treeview, GtkTreeModel *model, GtkTreeIter *iter)
{
    GtkTreePath *path;                      /* Chemin d'accès à la ligne   */

    path = gtk_tree_model_get_path(model, iter);

    gtk_tree_view_scroll_to_cell(treeview, path, NULL, FALSE, 0.0, 0.0);

    gtk_tree_path_free(path);

}
