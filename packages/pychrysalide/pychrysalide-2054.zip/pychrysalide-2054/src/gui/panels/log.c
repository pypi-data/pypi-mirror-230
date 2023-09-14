
/* Chrysalide - Outil d'analyse de fichiers binaires
 * log.c - panneau d'affichage des messages système
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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


#include "log.h"


#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <gtk/gtk.h>


#include "../panel-int.h"
#include "../core/panels.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/named.h"



/* Colonnes de la liste des messages */
typedef enum _LogColumn
{
    LGC_PICTURE,                            /* Image de représentation     */
    LGC_STRING,                             /* Chaîne de caractères        */

    LGC_COUNT                               /* Nombre de colonnes          */

} LogColumn;


/* Paramètres à transmettre pour un affichage */
typedef struct _log_data
{
    GPanelItem *item;                       /* Intermédiaire mis en place  */
    LogMessageType type;                    /* Type de message à afficher  */
    char *msg;                              /* Contenu du message          */

} log_data;


/* Panneau d'accueil (instance) */
struct _GLogPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

};


/* Panneau d'accueil (classe) */
struct _GLogPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Initialise la classe des panneaux d'affichage des messages. */
static void g_log_panel_class_init(GLogPanelClass *);

/* Initialise une instance de panneau d'affichage des messages. */
static void g_log_panel_init(GLogPanel *);

/* Supprime toutes les références externes. */
static void g_log_panel_dispose(GLogPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_log_panel_finalize(GLogPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_log_panel_class_get_key(const GLogPanelClass *);

/* Fournit une indication sur la personnalité du panneau. */
static PanelItemPersonality g_log_panel_class_get_personality(const GLogPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_log_panel_class_get_path(const GLogPanelClass *);

/* Indique la définition d'un éventuel raccourci clavier. */
static char *g_log_panel_class_get_key_bindings(const GLogPanelClass *);

/* Affiche un message dans le journal des messages système. */
static gboolean log_message(log_data *);



/* Indique le type défini pour un panneau d'affichage de messages. */
G_DEFINE_TYPE(GLogPanel, g_log_panel, G_TYPE_PANEL_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'affichage des messages.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_log_panel_class_init(GLogPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_log_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_log_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_log_panel_class_get_key;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_personality = (get_panel_personality_fc)g_log_panel_class_get_personality;
    panel->get_path = (get_panel_path_fc)g_log_panel_class_get_path;
    panel->get_bindings = (get_panel_bindings_fc)g_log_panel_class_get_key_bindings;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'affichage des messages. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_log_panel_init(GLogPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Messages"),
                                                                        _("Misc information"),
                                                                        PANEL_LOG_ID));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_log_panel_dispose(GLogPanel *panel)
{
    G_OBJECT_CLASS(g_log_panel_parent_class)->dispose(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_log_panel_finalize(GLogPanel *panel)
{
    G_OBJECT_CLASS(g_log_panel_parent_class)->finalize(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_log_panel_class_get_key(const GLogPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_LOG_ID);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication sur la personnalité du panneau.       *
*                                                                             *
*  Retour      : Identifiant lié à la nature unique du panneau.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PanelItemPersonality g_log_panel_class_get_personality(const GLogPanelClass *class)
{
    PanelItemPersonality result;            /* Personnalité à retourner    */

    result = PIP_PERSISTENT_SINGLETON;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique le chemin initial de la localisation d'un panneau.   *
*                                                                             *
*  Retour      : Chemin fixé associé à la position initiale.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_log_panel_class_get_path(const GLogPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("Ms");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique la définition d'un éventuel raccourci clavier.       *
*                                                                             *
*  Retour      : Description d'un raccourci ou NULL si aucun de défini.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_log_panel_class_get_key_bindings(const GLogPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("<Shift>F1");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau d'affichage des messages système.            *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_log_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_LOG_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                type  = espèce du message à ajouter.                         *
*                msg   = message à faire apparaître à l'écran.                *
*                                                                             *
*  Description : Affiche un message dans le journal des messages système.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_log_panel_add_message(GLogPanel *panel, LogMessageType type, const char *msg)
{
    log_data *data;                         /* Paramètres à joindre        */

    data = calloc(1, sizeof(log_data));

    data->item = G_PANEL_ITEM(panel);
    data->type = type;
    data->msg = strdup(msg);

    g_object_ref(G_OBJECT(data->item));

    g_main_context_invoke(NULL, (GSourceFunc)log_message, data);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = paramètres destinés à l'affichage d'un message.       *
*                                                                             *
*  Description : Affiche un message dans le journal des messages système.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Cette fonction, et c'est tout son intérêt, est toujours      *
*                exécutée dans le contexte GTK principal.                     *
*                                                                             *
******************************************************************************/

static gboolean log_message(log_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point d'insertion           */
    GtkTreeView *treeview;                  /* Affichage de la liste       */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(data->item)->widget));

    /* Mise en place du message */

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_append(store, &iter);

    switch (data->type)
    {
        case LMT_INFO:
            gtk_list_store_set(store, &iter,
                               LGC_PICTURE, "gtk-info",
                               LGC_STRING, data->msg,
                               -1);
            break;

        case LMT_PROCESS:
            gtk_list_store_set(store, &iter,
                               LGC_PICTURE, "gtk-execute",
                               LGC_STRING, data->msg,
                               -1);
            break;

        case LMT_WARNING:
            gtk_list_store_set(store, &iter,
                               LGC_PICTURE, "gtk-dialog-warning",
                               LGC_STRING, data->msg,
                               -1);
            break;

        case LMT_BAD_BINARY:
            gtk_list_store_set(store, &iter,
                               LGC_PICTURE, "gtk-dialog-warning",
                               LGC_STRING, data->msg,
                               -1);
            break;

        case LMT_ERROR:
        case LMT_EXT_ERROR:
            gtk_list_store_set(store, &iter,
                               LGC_PICTURE, "gtk-dialog-error",
                               LGC_STRING, data->msg,
                               -1);
            break;

        default:
            gtk_list_store_set(store, &iter,
                               LGC_STRING, data->msg,
                               -1);
            break;

    }

    /* Défilement pour pointer à l'affichage */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    scroll_to_treeview_iter(treeview, GTK_TREE_MODEL(store), &iter);

    g_object_unref(G_OBJECT(builder));

    /* Nettoyage de la mémoire */

    g_object_unref(G_OBJECT(data->item));

    free(data->msg);

    free(data);

    return G_SOURCE_REMOVE;

}
