
/* Chrysalide - Outil d'analyse de fichiers binaires
 * goto.c - boîte de dialogue pour les sauts à une adresse donnée
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


#include "goto.h"


#include <ctype.h>


#include <i18n.h>


#include "../core/global.h"
#include "../../analysis/binary.h"
#include "../../gtkext/easygtk.h"



/* Filtre les adresses en hexadécimal pendant l'édition. */
static void filter_addresses(GtkEntry *, const gchar *, gint, gint *, gpointer);

/* Clôture l'édition d'une adresse. */
static void validate_addresses(GtkEntry *, GtkDialog *);



/******************************************************************************
*                                                                             *
*  Paramètres  : entry    = composant GTK concerné par la procédure.          *
*                text     = nouveau texte inséré.                             *
*                length   = taille de ce texte.                               *
*                position = point d'insertion.                                *
*                data     = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Filtre les adresses en hexadécimal pendant l'édition.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void filter_addresses(GtkEntry *entry, const gchar *text, gint length, gint *position, gpointer data)
{
    gboolean has_hex;                       /* Préfixe '0x' déjà présent ? */
    gchar *filtered;                        /* Contenu nouveau approuvé    */
    gint count;                             /* Nouvelle taille validée     */
    gint i;                                 /* Boucle de parcours          */

    /**
     * On cherche à empêcher l'édition avant un '0x' présent,
     * ce qui viendrait fausser le fitrage.
     */
    has_hex = g_str_has_prefix(gtk_entry_get_text(entry), "0x");

    filtered = g_new(gchar, length);

    count = 0;

    for (i = 0; i < length; i++)
        switch (text[i])
        {
            case '0' ... '9':
            case 'a' ... 'f':
                if (!has_hex || ((i + *position) >= 2))
                    filtered[count++] = text[i];
                break;
            case 'A' ... 'F':
                if (!has_hex || ((i + *position) >= 2))
                    filtered[count++] = tolower(text[i]);
                break;
            case 'x':
            case 'X':
                if ((i + *position) == 1)
                    filtered[count++] = 'x';
                break;
        }

    if (count > 0)
    {
        g_signal_handlers_block_by_func(G_OBJECT(entry), G_CALLBACK(filter_addresses), data);
        gtk_editable_insert_text(GTK_EDITABLE(entry), filtered, count, position);
        g_signal_handlers_unblock_by_func(G_OBJECT(entry), G_CALLBACK(filter_addresses), data);
    }

    g_signal_stop_emission_by_name(G_OBJECT(entry), "insert_text");

    g_free(filtered);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry  = composant GTK concerné par la procédure.            *
*                dialog = boîte de dialogue à valider.                        *
*                                                                             *
*  Description : Clôture l'édition d'une adresse.                             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void validate_addresses(GtkEntry *entry, GtkDialog *dialog)
{
    gtk_dialog_response(dialog, GTK_RESPONSE_OK);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre parente à surpasser.                        *
*                                                                             *
*  Description : Construit la fenêtre de sélection des sections.              *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_goto_dialog(GtkWindow *parent)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkWidget *dlgvbox;                     /* Zone principale de la boîte */
    GtkWidget *vbox;                        /* Support à construire #1     */
    GtkWidget *label;                       /* Message d'introduction      */
    GtkWidget *combobox;                    /* Liste de sélection          */
    GtkWidget *entry;                       /* Zone de saisie principale   */
    GtkWidget *hbox;                        /* Support à construire #2     */
    GtkWidget *radio;                       /* Définition de localisation  */
    GLoadedBinary *binary;                  /* Binaire en cours d'édition  */
    vmpa2t *old_gotos;                      /* Liste de destinations       */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */
    bool is_virt;                           /* Détermination de l'utile    */
    VMPA_BUFFER(loc);                       /* Version humaintement lisible*/

    result = gtk_dialog_new();
    gtk_window_set_title(GTK_WINDOW(result), _("Go to address"));
    gtk_window_set_position(GTK_WINDOW(result), GTK_WIN_POS_CENTER);
    gtk_window_set_type_hint(GTK_WINDOW(result), GDK_WINDOW_TYPE_HINT_DIALOG);

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    dlgvbox = gtk_dialog_get_content_area(GTK_DIALOG(result));
    gtk_widget_show(dlgvbox);

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    gtk_widget_show(vbox);
    gtk_box_pack_start(GTK_BOX(dlgvbox), vbox, TRUE, TRUE, 0);
    gtk_container_set_border_width(GTK_CONTAINER(vbox), 8);

    /* Zone de saisie principale */

    label = qck_create_label(NULL, NULL, _("Enter the value of the target address:"));
    gtk_box_pack_start(GTK_BOX(vbox), label, TRUE, TRUE, 0);

    combobox = qck_create_combobox_with_entry(G_OBJECT(result), "combobox", NULL, NULL);
    gtk_box_pack_start(GTK_BOX(vbox), combobox, TRUE, TRUE, 0);

    entry = gtk_bin_get_child(GTK_BIN(combobox));

    g_signal_connect(G_OBJECT(entry), "insert_text",
                     G_CALLBACK(filter_addresses), NULL);
    g_signal_connect(G_OBJECT(entry), "activate",
                     G_CALLBACK(validate_addresses), GTK_DIALOG(result));

    /* Propriétés de la localisation */

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, TRUE, TRUE, 0);
    gtk_container_set_border_width(GTK_CONTAINER(hbox), 8);

    radio = qck_create_radio_button(G_OBJECT(result), "phy", _("Address is physical"),
                                          NULL, NULL, NULL);
    gtk_box_pack_start(GTK_BOX(hbox), radio, TRUE, TRUE, 0);

    radio = qck_create_radio_button(G_OBJECT(result), "virt", _("Address is virtual"),
                                          GTK_RADIO_BUTTON(radio), NULL, NULL);
    gtk_box_pack_start(GTK_BOX(hbox), radio, TRUE, TRUE, 0);

    /* Zone de validation */

    gtk_dialog_add_button(GTK_DIALOG(result), _("_Cancel"), GTK_RESPONSE_CANCEL);
    gtk_dialog_add_button(GTK_DIALOG(result), _("_Ok"), GTK_RESPONSE_OK);

    gtk_entry_set_text(GTK_ENTRY(entry), "0x");
    gtk_widget_grab_focus(entry);
    gtk_editable_set_position(GTK_EDITABLE(entry), -1);

    /* Restaurationd d'anciennes destinations */

    binary = G_LOADED_BINARY(get_current_content());
    old_gotos = g_loaded_binary_get_old_gotos(binary, &count);
    g_object_unref(G_OBJECT(binary));

    if (old_gotos != NULL)
    {
        for (i = 0; i < count; i++)
        {
            is_virt = has_virt_addr(&old_gotos[i]);

            if (is_virt)
                vmpa2_virt_to_string(&old_gotos[i], MDS_UNDEFINED, loc, NULL);
            else
                vmpa2_phys_to_string(&old_gotos[i], MDS_UNDEFINED, loc, NULL);

            gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combobox), loc);

        }

        free(old_gotos);

        gtk_combo_box_set_active(GTK_COMBO_BOX(combobox), 0);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dialog = boîte de dialogue ayant reçu une validation.        *
*                                                                             *
*  Description : Fournit l'adresse obtenue par la saisie de l'utilisateur.    *
*                                                                             *
*  Retour      : Adresse reccueillie par la boîte de dialogue.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *get_address_from_goto_dialog(GtkWidget *dialog)
{
    vmpa2t *result;                         /* Adresse à retourner         */
    GtkWidget *combobox;                    /* Liste de sélection          */
    GtkWidget *entry;                       /* Zone de saisie principale   */
    const gchar *text;                      /* Adresse en version texte    */
    GtkToggleButton *radio;                 /* Définition de localisation  */

    combobox = GTK_WIDGET(g_object_get_data(G_OBJECT(dialog), "combobox"));
    entry = gtk_bin_get_child(GTK_BIN(combobox));

    text = gtk_entry_get_text(GTK_ENTRY(entry));

    radio = GTK_TOGGLE_BUTTON(g_object_get_data(G_OBJECT(dialog), "phy"));

    if (gtk_toggle_button_get_active(radio))
        result = string_to_vmpa_phy(text);
    else
        result = string_to_vmpa_virt(text);

    return result;

}
