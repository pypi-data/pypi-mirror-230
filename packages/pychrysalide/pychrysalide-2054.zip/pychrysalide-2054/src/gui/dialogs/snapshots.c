
/* Chrysalide - Outil d'analyse de fichiers binaires
 * snapshots.c - gestion des instantanés de base de données
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "snapshots.h"


#include <assert.h>
#include <string.h>
#include <time.h>


#include <i18n.h>


#include "../../gtkext/easygtk.h"



/* Colonnes de l'arborescence d'instantanés */
typedef enum _SnapshotTreeColumn
{
    STC_ICON,                               /* Image de représentation     */
    STC_TITLE,                              /* Meilleure représentation    */

    STC_ID,                                 /* Identifiant de l'instantané */
    STC_TIMESTAMP,                          /* Valeur brute d'horodatage   */
    STC_NAME,                               /* Désignation de l'instantané */
    STC_DESC,                               /* Description de l'instantané */

} SnapshotTreeColumn;


/* Réagit à une fermeture de la boîte de dialogue. */
static void on_dialog_destroy(GtkWidget *, GtkBuilder *);

/* Réagit à un changement dans le choix du serveur. */
static void on_server_selection_changed(GtkComboBox *, GtkBuilder *);

/* Recherche un élément d'arborescence selon un identifiant. */
static bool find_suitable_parent(GtkTreeModel *, GtkTreeIter *, const char *, GtkTreeIter *);

/* Met à jour l'affichage avec une nouvelle liste d'instantanés. */
static void on_snapshots_updated(GAnalystClient *, GtkBuilder *);

/* Réinitialise la zone d'affichage des informations. */
static void reset_information_area(GtkBuilder *);

/* Active ou non l'accès à la zone d'affichage des informations. */
static void update_information_area_access(GtkBuilder *, bool);

/* Active ou non l'accès à la zone de contrôle des instantanés. */
static void update_control_area_access(GtkBuilder *, bool, bool, bool);

/* Met à jour l'affichage des informations d'un instantané. */
static void on_tree_selection_changed(GtkTreeSelection *, GtkBuilder *);

/* Restaure sur demande un nouvel instantané. */
static void restore_old_snapshot(GtkToolButton *, GtkBuilder *);

/* Crée sur demande un nouvel instantané. */
static void create_new_snapshot(GtkToolButton *, GtkBuilder *);

/* Supprime sur demande un instantané. */
static void remove_old_snapshot(GtkToolButton *, GtkBuilder *);

/* Supprime sur demande un instantané et ses successeurs. */
static void delete_old_snapshot(GtkToolButton *, GtkBuilder *);

/* Applique à un instantané ses nouvelles informations. */
static void apply_new_snapshot_info(GtkButton *, GtkBuilder *);

/* Ferme la boîte de dialogue. */
static void close_dialog_box(GtkButton *, GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire chargé en mémoire à traiter.                *
*                parent = fenêtre principale de l'éditeur.                    *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Affiche un gestionnaire d'instantanés de base de données.    *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_snapshots_dialog(GLoadedBinary *binary, GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GFile *file;                            /* Accès à une image interne   */
    GIcon *icon;                            /* Image de représentation     */
    GtkComboBox *combo;                     /* Liste de serveurs           */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/snapshots.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    g_object_ref(G_OBJECT(result));
    g_object_set_data_full(G_OBJECT(builder), "window", result, g_object_unref);

    g_object_ref(G_OBJECT(binary));
    g_object_set_data_full(G_OBJECT(builder), "binary", binary, g_object_unref);

    file = g_file_new_for_uri("resource:///org/chrysalide/gui/core/images/snapshot.png");
    icon = g_file_icon_new(file);
    g_object_set_data_full(G_OBJECT(builder), "icon", icon, g_object_unref);

    file = g_file_new_for_uri("resource:///org/chrysalide/gui/core/images/snapshot_current.png");
    icon = g_file_icon_new(file);
    g_object_set_data_full(G_OBJECT(builder), "current_icon", icon, g_object_unref);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_dialog_destroy),
                                     BUILDER_CALLBACK(on_server_selection_changed),
                                     BUILDER_CALLBACK(on_tree_selection_changed),
                                     BUILDER_CALLBACK(restore_old_snapshot),
                                     BUILDER_CALLBACK(create_new_snapshot),
                                     BUILDER_CALLBACK(remove_old_snapshot),
                                     BUILDER_CALLBACK(delete_old_snapshot),
                                     BUILDER_CALLBACK(apply_new_snapshot_info),
                                     BUILDER_CALLBACK(close_dialog_box),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    /* Mise à jour de l'interface */

    reset_information_area(builder);
    update_control_area_access(builder, false, false, false);

    combo = GTK_COMBO_BOX(gtk_builder_get_object(builder, "servers"));

    gtk_combo_box_set_active(combo, 0);

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : dialog  = fenêtre en cours de suppression.                   *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à une fermeture de la boîte de dialogue.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dialog_destroy(GtkWidget *dialog, GtkBuilder *builder)
{
    GAnalystClient *client;                 /* Cible des interactions      */

    /* Déconnexion de l'ancien */

    client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

    if (client != NULL)
        g_signal_handlers_disconnect_by_func(client, on_snapshots_updated, builder);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : combo   = liste de sélection à l'origine de la procédure.    *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à un changement dans le choix du serveur.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_server_selection_changed(GtkComboBox *combo, GtkBuilder *builder)
{
    GAnalystClient *client;                 /* Cible des interactions      */
    gint active;                            /* Indice du serveur retenu    */
    GLoadedBinary *binary;                  /* Binaire en cours d'étude    */
    GtkTreeStore *store;                    /* Modèle de gestion           */

    /* Déconnexion de l'ancien */

    client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

    if (client != NULL)
        g_signal_handlers_disconnect_by_func(client, on_snapshots_updated, builder);

    /* Connexion nouvelle */

    active = gtk_combo_box_get_active(combo);

    binary = G_LOADED_BINARY(g_object_get_data(G_OBJECT(builder), "binary"));

    client = g_loaded_binary_get_client(binary);

    if (client == NULL)
    {
        g_object_set_data(G_OBJECT(builder), "client", NULL);

        store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));
        gtk_tree_store_clear(store);

        reset_information_area(builder);
        update_control_area_access(builder, false, false, false);

    }

    else
    {
        g_object_ref(G_OBJECT(client));
        g_object_set_data_full(G_OBJECT(builder), "client", client, g_object_unref);

        g_signal_connect(client, "snapshots-updated", G_CALLBACK(on_snapshots_updated), builder);
        g_signal_connect(client, "snapshot-changed", G_CALLBACK(on_snapshots_updated), builder);

        on_snapshots_updated(client, builder);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model = modèle de gestion de données à consulter.            *
*                iter  = point de départ des recherches.                      *
*                id    = identifiant de l'instantané recherché.               *
*                found = emplacement de l'éventuel noeud trouvé. [OUT]        *
*                                                                             *
*  Description : Recherche un élément d'arborescence selon un identifiant.    *
*                                                                             *
*  Retour      : true pour indiquer une recherche fructueuse, false sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool find_suitable_parent(GtkTreeModel *model, GtkTreeIter *iter, const char *id, GtkTreeIter *found)
{
    bool result;                            /* Bilan à retourner           */
    gchar *value;                           /* Identifiant courant         */
    gint count;                             /* Quantité de fils présents   */
    gint i;                                 /* Boucle de parcours          */
    GtkTreeIter child;                      /* Localisation d'un fils      */
#ifndef NDEBUG
    gboolean status;                        /* Bilan d'une consultation    */
#endif

    gtk_tree_model_get(model, iter, STC_ID, &value, -1);

    result = (strcmp(value, id) == 0);

    g_free(value);

    if (result)
        *found = *iter;

    else
    {
        count = gtk_tree_model_iter_n_children(model, iter);

        for (i = 0; i < count && !result; i++)
        {
#ifndef NDEBUG
            status = gtk_tree_model_iter_nth_child(model, &child, iter, i);
            assert(status);
#else
            gtk_tree_model_iter_nth_child(model, &child, iter, i);
#endif

            result = find_suitable_parent(model, &child, id, found);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client  = client connecté à l'origine de la procédure.       *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Met à jour l'affichage avec une nouvelle liste d'instantanés.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_snapshots_updated(GAnalystClient *client, GtkBuilder *builder)
{
    GtkTreeStore *store;                    /* Modèle de gestion           */
    snapshot_info_t *info;                  /* Liste d'instantanés présents*/
    size_t count;                           /* Taille de cette liste       */
    bool status;                            /* Validité de cet identifiant */
    size_t i;                               /* Boucle de parcours          */
    char *id;                               /* Identifiant du parent       */
    GtkTreeIter iter;                       /* Point d'insertion           */
#ifndef NDEBUG
    gboolean check;                         /* Vérification par principe   */
#endif
    GtkTreeIter parent;                     /* Parent du point d'insertion */
    GIcon *icon;                            /* Image de représentation     */
    char *name;                             /* Désignation d'instantané    */
    snapshot_id_t current;                  /* Instantané courant          */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    const char *raw;                        /* Identifiant brut            */
    GtkTreeSelection *selection;            /* Gestionnaire de sélection   */

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_store_clear(store);

    status = g_analyst_client_get_snapshots(client, &info, &count);

    if (!status)
    {
        reset_information_area(builder);
        update_control_area_access(builder, false, false, false);
    }

    else
    {
        /* Remplissage */

        for (i = 0; i < count; i++)
        {
            id = snapshot_id_as_string(get_snapshot_info_parent_id(&info[i]));

            if (strcmp(id, NO_SNAPSHOT_ROOT) == 0)
                gtk_tree_store_append(store, &iter, NULL);

            else
            {
#ifndef NDEBUG
                check = gtk_tree_model_get_iter_first(GTK_TREE_MODEL(store), &iter);
                assert(check);
#else
                gtk_tree_model_get_iter_first(GTK_TREE_MODEL(store), &iter);
#endif

                status = find_suitable_parent(GTK_TREE_MODEL(store), &iter, id, &parent);
                assert(status);

                gtk_tree_store_append(store, &iter, &parent);

            }

            id = snapshot_id_as_string(get_snapshot_info_id(&info[i]));

            icon = G_ICON(g_object_get_data(G_OBJECT(builder), "icon"));

            name = get_snapshot_info_name(&info[i]);

            gtk_tree_store_set(store, &iter,
                               STC_ICON, icon,
                               STC_TITLE, name != NULL ? name : id,
                               STC_ID, id,
                               STC_TIMESTAMP, get_snapshot_info_created(&info[i]),
                               STC_NAME, name,
                               STC_DESC, get_snapshot_info_desc(&info[i]),
                               -1);

            exit_snapshot_info(&info[i]);

        }

        free(info);

        /* Ajout de l'instantané courant */

        status = g_analyst_client_get_current_snapshot(client, &current);

        if (status)
        {
            id = snapshot_id_as_string(&current);

#ifndef NDEBUG
            check = gtk_tree_model_get_iter_first(GTK_TREE_MODEL(store), &iter);
            assert(check);
#else
            gtk_tree_model_get_iter_first(GTK_TREE_MODEL(store), &iter);
#endif

            status = find_suitable_parent(GTK_TREE_MODEL(store), &iter, id, &parent);

            if (status)
            {
                gtk_tree_store_append(store, &iter, &parent);

                icon = G_ICON(g_object_get_data(G_OBJECT(builder), "current_icon"));

                gtk_tree_store_set(store, &iter,
                                   STC_ICON, icon,
                                   STC_TITLE, _("Current"),
                                   -1);

            }

        }

        /* Plein affichage */

        treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

        gtk_tree_view_expand_all(treeview);

        /* Remise en place de la dernière sélection */

        raw = g_object_get_data(G_OBJECT(builder), "selected");

        if (raw != NULL)
        {
#ifndef NDEBUG
            check = gtk_tree_model_get_iter_first(GTK_TREE_MODEL(store), &iter);
            assert(check);
#else
            gtk_tree_model_get_iter_first(GTK_TREE_MODEL(store), &iter);
#endif

            status = find_suitable_parent(GTK_TREE_MODEL(store), &iter, raw, &iter);

            if (status)
            {
                selection = gtk_tree_view_get_selection(treeview);

                gtk_tree_selection_select_iter(selection, &iter);

            }

            else
            {
                reset_information_area(builder);

                update_control_area_access(builder, false, false, false);

                g_object_set_data(G_OBJECT(builder), "selected", NULL);

            }

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réinitialise la zone d'affichage des informations.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reset_information_area(GtkBuilder *builder)
{
    GtkLabel *label;                        /* Etiquette à faire évoluer   */
    GtkEntry *entry;                        /* Zone de saisie à actualiser */

    label = GTK_LABEL(gtk_builder_get_object(builder, "identifier"));
    gtk_label_set_text(label, "-");

    label = GTK_LABEL(gtk_builder_get_object(builder, "timestamp"));
    gtk_label_set_text(label, "-");

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "name"));
    gtk_entry_set_text(entry, "");

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "description"));
    gtk_entry_set_text(entry, "");

    update_information_area_access(builder, false);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = espace de référencement global.                    *
*                state   = état des possibilités d'interactions à appliquer.  *
*                                                                             *
*  Description : Active ou non l'accès à la zone d'affichage des informations.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_information_area_access(GtkBuilder *builder, bool state)
{
    GtkWidget *widget;                      /* Composant à traiter         */

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "identifier"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "timestamp"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "name"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "description"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "apply"));
    gtk_widget_set_sensitive(widget, state);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = espace de référencement global.                    *
*                restore = accès à la restauration d'un instantané.           *
*                create  = accès à la création d'un nouvel instantané.        *
*                delete  = accès à la suppression d'instantanés.              *
*                                                                             *
*  Description : Active ou non l'accès à la zone de contrôle des instantanés. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_control_area_access(GtkBuilder *builder, bool restore, bool create, bool delete)
{
    GtkWidget *widget;                      /* Composant à traiter         */

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "restore"));
    gtk_widget_set_sensitive(widget, restore);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "create"));
    gtk_widget_set_sensitive(widget, create);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "remove"));
    gtk_widget_set_sensitive(widget, delete);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "delete"));
    gtk_widget_set_sensitive(widget, delete);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = nouvelle sélection à appliquer.                  *
*                builder   = espace de référencement global.                  *
*                                                                             *
*  Description : Met à jour l'affichage des informations d'un instantané.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_tree_selection_changed(GtkTreeSelection *selection, GtkBuilder *builder)
{
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point de sélection          */
    gchar *id;                              /* Identifiant d'instantané    */
    guint64 timestamp;                      /* Horodatage associé          */
    gchar *name;                            /* Eventuelle désignation      */
    gchar *desc;                            /* Eventuelle description      */
    GtkLabel *label;                        /* Etiquette à faire évoluer   */
    char buf[27];                           /* Tampon pour la date         */
    GtkEntry *entry;                        /* Zone de saisie à actualiser */
    gboolean is_not_root;                   /* Particularité de sélection  */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter,
                           STC_ID, &id,
                           STC_TIMESTAMP, &timestamp,
                           STC_NAME, &name,
                           STC_DESC, &desc,
                           -1);

        if (id == NULL)
        {
            assert(name == NULL);
            assert(desc == NULL);

            reset_information_area(builder);

            update_control_area_access(builder, false, true, false);

            g_object_set_data(G_OBJECT(builder), "selected", NULL);

        }

        else
        {
            label = GTK_LABEL(gtk_builder_get_object(builder, "identifier"));
            gtk_label_set_text(label, id);

            ctime_r((time_t []) { timestamp /  1000000 }, buf);
            buf[strlen(buf) - 1] = 0;

            label = GTK_LABEL(gtk_builder_get_object(builder, "timestamp"));
            gtk_label_set_text(label, buf);

            entry = GTK_ENTRY(gtk_builder_get_object(builder, "name"));
            gtk_entry_set_text(entry, name != NULL ? name : "");

            if (name != NULL)
                g_free(name);

            entry = GTK_ENTRY(gtk_builder_get_object(builder, "description"));
            gtk_entry_set_text(entry, desc != NULL ? desc : "");

            if (desc != NULL)
                g_free(desc);

            update_information_area_access(builder, true);

            is_not_root = gtk_tree_model_iter_parent(model, (GtkTreeIter []) { { 0 } }, &iter);

            update_control_area_access(builder, true, false, is_not_root);

            g_object_set_data_full(G_OBJECT(builder), "selected", id, g_free);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant GTK à l'origine de la procédure.         *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Restaure sur demande un nouvel instantané.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void restore_old_snapshot(GtkToolButton *button, GtkBuilder *builder)
{
    const char *raw;                        /* Identifiant brut            */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'une conversion      */
    GAnalystClient *client;                 /* Cible des interactions      */

    raw = g_object_get_data(G_OBJECT(builder), "selected");

    status = init_snapshot_id_from_text(&id, raw);

    if (status)
    {
        client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

        g_analyst_client_restore_snapshot(client, &id);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant GTK à l'origine de la procédure.         *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Crée sur demande un nouvel instantané.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void create_new_snapshot(GtkToolButton *button, GtkBuilder *builder)
{
    GAnalystClient *client;                 /* Cible des interactions      */

    client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

    g_analyst_client_create_snapshot(client);

}

/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant GTK à l'origine de la procédure.         *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Supprime sur demande un instantané.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void remove_old_snapshot(GtkToolButton *button, GtkBuilder *builder)
{
    const char *raw;                        /* Identifiant brut            */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'une conversion      */
    GAnalystClient *client;                 /* Cible des interactions      */

    raw = g_object_get_data(G_OBJECT(builder), "selected");

    status = init_snapshot_id_from_text(&id, raw);

    if (status)
    {
        client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

        g_analyst_client_remove_snapshot(client, &id, false);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant GTK à l'origine de la procédure.         *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Supprime sur demande un instantané et ses successeurs.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_old_snapshot(GtkToolButton *button, GtkBuilder *builder)
{
    const char *raw;                        /* Identifiant brut            */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'une conversion      */
    GAnalystClient *client;                 /* Cible des interactions      */

    raw = g_object_get_data(G_OBJECT(builder), "selected");

    status = init_snapshot_id_from_text(&id, raw);

    if (status)
    {
        client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

        g_analyst_client_remove_snapshot(client, &id, true);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant GTK à l'origine de la procédure.         *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Applique à un instantané ses nouvelles informations.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void apply_new_snapshot_info(GtkButton *button, GtkBuilder *builder)
{
    const char *raw;                        /* Identifiant brut            */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'une conversion      */
    GAnalystClient *client;                 /* Cible des interactions      */
    GtkEntry *entry;                        /* Zone de saisie à actualiser */

    raw = g_object_get_data(G_OBJECT(builder), "selected");

    status = init_snapshot_id_from_text(&id, raw);

    if (status)
    {
        client = G_ANALYST_CLIENT(g_object_get_data(G_OBJECT(builder), "client"));

        entry = GTK_ENTRY(gtk_builder_get_object(builder, "name"));
        g_analyst_client_set_snapshot_name(client, &id, gtk_entry_get_text(entry));

        entry = GTK_ENTRY(gtk_builder_get_object(builder, "description"));
        g_analyst_client_set_snapshot_desc(client, &id, gtk_entry_get_text(entry));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = composant GTK à l'origine de la procédure.         *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Ferme la boîte de dialogue.                                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void close_dialog_box(GtkButton *button, GtkBuilder *builder)
{
    GtkDialog *dialog;                      /* Fenêtre à manipuler         */

    dialog = GTK_DIALOG(gtk_builder_get_object(builder, "window"));

    gtk_dialog_response(dialog, GTK_RESPONSE_CLOSE);

}
