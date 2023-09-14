
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panel.c - gestion des éléments réactifs spécifiques aux panneaux
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "panel.h"


#include <assert.h>
#include <stdio.h>
#include <string.h>


#include "panel-int.h"
#include "core/global.h"
#include "core/items.h"
#include "../common/extstr.h"
#include "../core/params.h"
#include "../gtkext/gtkdockable-int.h"
#include "../gtkext/named.h"
#include "../plugins/dt.h"
#include "../plugins/pglist.h"



/* ------------------------- COEUR DES PANNEAUX D'AFFICHAGE ------------------------- */


/* Initialise la classe des panneaux graphiques de l'éditeur. */
static void g_panel_item_class_init(GPanelItemClass *);

/* Initialise une instance de panneau graphique pour l'éditeur. */
static void g_panel_item_init(GPanelItem *);

/* Procède à l'initialisation de l'interface d'incrustation. */
static void g_panel_item_dockable_interface_init(GtkDockableInterface *);

/* Supprime toutes les références externes. */
static void g_panel_item_dispose(GPanelItem *);

/* Procède à la libération totale de la mémoire. */
static void g_panel_item_finalize(GPanelItem *);

/* Construit la chaîne d'accès à un élément de configuration. */
static char *gtk_panel_item_class_build_configuration_key(const GPanelItemClass *, const char *);

/* Fournit le nom court du composant encapsulable. */
static char *gtk_panel_item_get_name(const GPanelItem *);

/* Fournit le nom long du composant encapsulable. */
static char *gtk_panel_item_get_desc(const GPanelItem *);

/* Détermine si un panneau peut être filtré. */
static bool gtk_panel_item_can_search(const GPanelItem *);

/* Fournit le composant graphique intégrable dans un ensemble. */
static GtkWidget *gtk_panel_item_get_widget(GPanelItem *);

/* Démarre l'actualisation du filtrage du contenu. */
static void gtk_panel_item_update_filtered(GPanelItem *, const char *);



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Présente une copie de l'affichage du composant rafraîchi. */
static gboolean g_panel_item_draw_mask(GtkWidget *, cairo_t *, GPanelItem *);



/* ---------------------------------------------------------------------------------- */
/*                           COEUR DES PANNEAUX D'AFFICHAGE                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un élément destiné à un panneau. */
G_DEFINE_TYPE_WITH_CODE(GPanelItem, g_panel_item, G_TYPE_EDITOR_ITEM,
                        G_IMPLEMENT_INTERFACE(GTK_TYPE_DOCKABLE, g_panel_item_dockable_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux graphiques de l'éditeur.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_item_class_init(GPanelItemClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_panel_item_dispose;
    object->finalize = (GObjectFinalizeFunc)g_panel_item_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_widget = (get_item_widget_fc)gtk_panel_item_get_widget;

    class->get_personality = gtk_panel_item_class_get_personality_singleton;
    class->dock_at_startup = gtk_panel_item_class_return_true;
    class->can_search = gtk_panel_item_class_return_false;

    g_signal_new("dock-request",
                 G_TYPE_PANEL_ITEM,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GPanelItemClass, dock_request),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

    g_signal_new("undock-request",
                 G_TYPE_PANEL_ITEM,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GPanelItemClass, undock_request),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de panneau graphique pour l'éditeur. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_item_init(GPanelItem *item)
{
    item->docked = false;

    item->widget = NULL;
    item->cached_widget = NULL;

    item->filter = NULL;

    g_atomic_int_set(&item->switched, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GTK à initialiser.                         *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface d'incrustation.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_item_dockable_interface_init(GtkDockableInterface *iface)
{
    iface->get_name = (get_dockable_name_fc)gtk_panel_item_get_name;
    iface->get_desc = (get_dockable_desc_fc)gtk_panel_item_get_desc;
    iface->can_search = (can_dockable_search_fc)gtk_panel_item_can_search;

    iface->get_widget = (get_dockable_widget_fc)gtk_panel_item_get_widget;
    iface->update_filtered = (update_filtered_data_fc)gtk_panel_item_update_filtered;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_item_dispose(GPanelItem *item)
{
    g_clear_object(&item->widget);
    g_clear_object(&item->cached_widget);

    G_OBJECT_CLASS(g_panel_item_parent_class)->dispose(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_panel_item_finalize(GPanelItem *item)
{
    if (item->filter != NULL)
        free(item->filter);

    if (item->surface != NULL)
        cairo_surface_destroy(item->surface);

    G_OBJECT_CLASS(g_panel_item_parent_class)->finalize(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication sur la personnalité du panneau.       *
*                                                                             *
*  Retour      : Identifiant lié à la nature du panneau.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PanelItemPersonality gtk_panel_item_class_get_personality(const GPanelItemClass *class)
{
    PanelItemPersonality result;            /* Personnalité à retourner    */

    result = class->get_personality(class);

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

PanelItemPersonality gtk_panel_item_class_get_personality_singleton(const GPanelItemClass *class)
{
    PanelItemPersonality result;            /* Personnalité à retourner    */

    result = PIP_SINGLETON;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication d'accroche du panneau au démarrage.   *
*                                                                             *
*  Retour      : true si le panneau doit être affiché de prime abord.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_panel_item_class_dock_at_startup(const GPanelItemClass *class)
{
    bool result;                            /* Statut à retourner          */
    GGenConfig *config;                     /* Configuration courante      */
    char *key;                              /* Clef d'accès à un paramètre */
#ifndef NDEBUG
    bool status;                            /* Bilan de consultation       */
#endif

    config = get_main_configuration();

    key = gtk_panel_item_class_build_configuration_key(class, "dock_at_startup");

#ifndef NDEBUG
    status = g_generic_config_get_value(config, key, &result);
    assert(status);
#else
    g_generic_config_get_value(config, key, &result);
#endif

    free(key);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe associée à la consultation.                   *
*                                                                             *
*  Description : Renvoie false lors d'une consultation de la classe.          *
*                                                                             *
*  Retour      : false.                                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_panel_item_class_return_false(const GPanelItemClass *class)
{
    bool result;                            /* Statut à retourner          */

    result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe associée à la consultation.                   *
*                                                                             *
*  Description : Renvoie true lors d'une consultation de la classe.           *
*                                                                             *
*  Retour      : true.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_panel_item_class_return_true(const GPanelItemClass *class)
{
    bool result;                            /* Statut à retourner          */

    result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Détermine si un panneau peut être filtré.                    *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_panel_item_class_can_search(const GPanelItemClass *class)
{
    bool result;                            /* Statut à retourner          */

    result = class->can_search(class);

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

char *gtk_panel_item_class_get_path(const GPanelItemClass *class)
{
    char *result;                           /* Emplacement à retourner     */
    GGenConfig *config;                     /* Configuration courante      */
    char *key;                              /* Clef d'accès à un paramètre */
    const char *path;                       /* Nouveau chemin de placement */
#ifndef NDEBUG
    bool status;                            /* Statut de l'encapsulation   */
#endif

    config = get_main_configuration();

    key = gtk_panel_item_class_build_configuration_key(class, "path");

#ifndef NDEBUG
    status = g_generic_config_get_value(config, key, &path);
    assert(status);
#else
    g_generic_config_get_value(config, key, &path);
#endif

    free(key);

    result = strdup(path);

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

char *gtk_panel_item_class_get_key_bindings(const GPanelItemClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    if (class->get_bindings != NULL)
        result = class->get_bindings(class);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe du type de panneau à traiter.                *
*                attrib = élément de configuration à inclure dans le résultat.*
*                                                                             *
*  Description : Construit la chaîne d'accès à un élément de configuration.   *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *gtk_panel_item_class_build_configuration_key(const GPanelItemClass *class, const char *attrib)
{
    char *result;                           /* Construction à renvoyer     */
    const char *name;                       /* Nom court du panneau        */

    name = g_editor_item_class_get_key(G_EDITOR_ITEM_CLASS(class));

    asprintf(&result, "gui.panels.%s.%s", attrib, name);

    result = strrpl(result, " ", "_");

    result = strlower(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe de panneau à consulter.                      *
*                config = configuration à compléter.                          *
*                                                                             *
*  Description : Met en place les bases de la configuration d'un panneau.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool gtk_panel_item_class_setup_configuration(const GPanelItemClass *class, GGenConfig *config)
{
    bool result;                            /* Bilan à retourner           */
    char *key;                              /* Clef d'accès à un paramètre */
    bool dock_at_startup;                   /* Affichage dès le départ ?   */
    char *path;                             /* Localisation du panneau     */

    key = gtk_panel_item_class_build_configuration_key(class, "dock_at_startup");

    dock_at_startup = class->dock_at_startup(class);

    result = g_generic_config_create_param_if_not_exist(config, key, CPT_BOOLEAN, dock_at_startup);

    free(key);

    if (!result)
        goto exit;

    key = gtk_panel_item_class_build_configuration_key(class, "path");

    path = class->get_path(class);

    result = g_generic_config_create_param_if_not_exist(config, key, CPT_STRING, path);

    free(path);

    free(key);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de panneau à mettre en place.                    *
*                path = emplacement d'affichage ou NULL.                      *
*                                                                             *
*  Description : Crée un élément de panneau réactif.                          *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_panel_item_new(GType type, const char *path)
{
    GPanelItem *result;                     /* Structure à retourner       */
    GPanelItemClass *class;                 /* Classe associée au type     */
    PanelItemPersonality personality;       /* Caractéristique de panneau  */
    GtkTiledGrid *grid;                     /* Composant d'affichage       */

    class = g_type_class_ref(type);

    personality = gtk_panel_item_class_get_personality(class);
    assert(path != NULL || personality == PIP_PERSISTENT_SINGLETON);

    g_type_class_unref(class);

    if (personality == PIP_PERSISTENT_SINGLETON || personality == PIP_SINGLETON)
    {
        result = G_PANEL_ITEM(find_editor_item_by_type(type));

        if (result != NULL)
            goto singleton;

    }

    result = create_object_from_type(type);

    grid = get_tiled_grid();

    g_signal_connect_swapped(result, "dock-request", G_CALLBACK(gtk_tiled_grid_add), grid);
    g_signal_connect_swapped(result, "undock-request", G_CALLBACK(gtk_tiled_grid_remove), grid);

    gtk_dockable_setup_dnd(GTK_DOCKABLE(result));

    register_editor_item(G_EDITOR_ITEM(result));

    notify_panel_creation(result);

 singleton:

    if (path != NULL)
    {
        if (path[0] != '\0')
            gtk_panel_item_set_path(result, path);

        g_panel_item_dock(result);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance de panneau à consulter.                      *
*                                                                             *
*  Description : Indique le composant graphique principal du panneau.         *
*                                                                             *
*  Retour      : Composant graphique avec nom constituant le panneau.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GNamedWidget *gtk_panel_item_get_named_widget(const GPanelItem *item)
{
    GNamedWidget *result;                   /* Composant nommé à retourner */

    result = item->widget;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance GTK dont l'interface est à consulter.        *
*                                                                             *
*  Description : Fournit le nom court du composant encapsulable.              *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *gtk_panel_item_get_name(const GPanelItem *item)
{
    char *result;                           /* Désignation à retourner     */

    result = g_named_widget_get_name(G_NAMED_WIDGET(item->widget), false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance GTK dont l'interface est à consulter.        *
*                                                                             *
*  Description : Fournit le nom long du composant encapsulable.               *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *gtk_panel_item_get_desc(const GPanelItem *item)
{
    char *result;                           /* Description à retourner     */

    result = g_named_widget_get_name(G_NAMED_WIDGET(item->widget), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance GTK dont l'interface est à consulter.        *
*                                                                             *
*  Description : Détermine si un panneau peut être filtré.                    *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool gtk_panel_item_can_search(const GPanelItem *item)
{
    bool result;                            /* Indication à retourner      */
    GPanelItemClass *class;                 /* Classe de l'élément visé    */

    class = G_PANEL_ITEM_GET_CLASS(item);

    result = gtk_panel_item_class_can_search(class);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance GTK dont l'interface est à consulter.        *
*                                                                             *
*  Description : Fournit le composant graphique intégrable dans un ensemble.  *
*                                                                             *
*  Retour      : Composant graphique prêt à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *gtk_panel_item_get_widget(GPanelItem *item)
{
    GtkWidget *result;                      /* Composant à retourner       */

    if (item->cached_widget == NULL)
        item->cached_widget = g_named_widget_get_widget(G_NAMED_WIDGET(item->widget));

    result = item->cached_widget;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance GTK dont l'interface est à sollicitée.       *
*                                                                             *
*  Description : Démarre l'actualisation du filtrage du contenu.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_panel_item_update_filtered(GPanelItem *item, const char *filter)
{
    assert(gtk_panel_item_can_search(item));

    if (item->filter != NULL)
        free(item->filter);

    item->filter = (filter ? strdup(filter) : NULL);

    G_PANEL_ITEM_GET_CLASS(item)->update_filtered(item);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance GTK à consulter.                             *
*                path = nouvelle emplacement d'inclusion.                     *
*                                                                             *
*  Description : Définit le chemin d'accès à utiliser pour les encapsulations.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_panel_item_set_path(GPanelItem *item, const char *path)
{
    GGenConfig *config;                     /* Configuration courante      */
    char *key;                              /* Clef d'accès à un paramètre */

    config = get_main_configuration();

    key = gtk_panel_item_class_build_configuration_key(G_PANEL_ITEM_GET_CLASS(item), "path");

    g_generic_config_set_value(config, key, path);

    free(key);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = composant à présenter à l'affichage.                  *
*                                                                             *
*  Description : Place un panneau dans l'ensemble affiché.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_panel_item_dock(GPanelItem *item)
{
    assert(!item->docked);

    g_signal_emit_by_name(item, "dock-request");

    if (G_PANEL_ITEM_GET_CLASS(item)->ack_dock != NULL)
        G_PANEL_ITEM_GET_CLASS(item)->ack_dock(item);

    notify_panel_docking(item, true);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = composant d'affichage à mettre à jour.                *
*                status = nouvel état d'encapsulation.                        *
*                                                                             *
*  Description : Définit si le composant repose sur un support de l'éditeur.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_panel_item_set_dock_at_startup(GPanelItem *item, bool status)
{
    char *key;                              /* Clef d'accès à un paramètre */

    item->docked = status;

    key = gtk_panel_item_class_build_configuration_key(G_PANEL_ITEM_GET_CLASS(item), "dock_at_startup");

    g_generic_config_set_value(get_main_configuration(), key, status);

    free(key);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = composant d'affichage à consulter.                    *
*                                                                             *
*  Description : Indique si le composant repose sur un support de l'éditeur.  *
*                                                                             *
*  Retour      : true si le composant est bien incrusté quelque part.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_panel_item_is_docked(const GPanelItem *item)
{
    bool result;                            /* Status à retourner          */

    result = item->docked;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = composant à retirer de l'affichage.                   *
*                                                                             *
*  Description : Supprime un panneau de l'ensemble affiché.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_panel_item_undock(GPanelItem *item)
{
    PanelItemPersonality personality;       /* Caractéristique de panneau  */

    assert(item->docked);

    g_signal_emit_by_name(item, "undock-request");

    if (G_PANEL_ITEM_GET_CLASS(item)->ack_undock != NULL)
        G_PANEL_ITEM_GET_CLASS(item)->ack_undock(item);

    notify_panel_docking(item, false);

    personality = gtk_panel_item_class_get_personality(G_PANEL_ITEM_GET_CLASS(item));

    if (personality != PIP_PERSISTENT_SINGLETON)
        unregister_editor_item(G_EDITOR_ITEM(item));

}



/* ---------------------------------------------------------------------------------- */
/*                        MECANISMES DE MISE A JOUR DE PANNEAU                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item = panneau ciblé par une mise à jour.                    *
*                                                                             *
*  Description : Obtient le groupe de travail dédié à une mise à jour.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t g_panel_item_get_group(const GPanelItem *item)
{
    wgroup_id_t result;                     /* Identifiant à retourner     */

    result = G_PANEL_ITEM_GET_CLASS(item)->gid;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique sur lequel dessiner.            *
*                cr     = contexte graphique pour le dessin.                  *
*                panel = panneau ciblé par une mise à jour.                   *
*                                                                             *
*  Description : Présente une copie de l'affichage du composant rafraîchi.    *
*                                                                             *
*  Retour      : FALSE afin de poursuivre les traitements.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean g_panel_item_draw_mask(GtkWidget *widget, cairo_t *cr, GPanelItem *item)
{
    int width;                              /* Largeur du composant actuel */
    int height;                             /* Hauteur du composant actuel */

    width = gtk_widget_get_allocated_width(widget);
    height = gtk_widget_get_allocated_height(widget);

    cairo_save(cr);

    cairo_set_source_surface(cr, item->surface, 0, 0);
    cairo_rectangle(cr, 0, 0, width, height);

    cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE);
    cairo_fill(cr);

    cairo_restore(cr);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau avant sa mise à jour.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_panel_item_switch_to_updating_mask(GPanelItem *item)
{
    GtkBuilder *builder;                    /* Constructeur sous-jacent    */
    GtkWidget *content;                     /* Composant à faire évoluer   */
    GdkWindow *window;                      /* Fenêtre au contenu à copier */
    int width;                              /* Largeur du composant actuel */
    int height;                             /* Hauteur du composant actuel */
    cairo_t *cr;                            /* Pinceau pour les dessins    */
    GtkAdjustment *adj;                     /* Défilement éventuel         */
    GtkStack *stack;                        /* Pile de composants GTK      */
    GtkWidget *mask;                        /* Masque des travaux          */

    if (g_atomic_int_add(&item->switched, 1) > 0)
        return;

    /* Copie de l'affichage courant */

    assert(item->surface == NULL);

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(item->widget));

    content = GTK_WIDGET(gtk_builder_get_object(builder, "content"));

    window = gtk_widget_get_window(content);

    if (window != NULL)
    {
        width = gtk_widget_get_allocated_width(content);
        height = gtk_widget_get_allocated_height(content);

        item->surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height);

        cr = cairo_create(item->surface);

        gdk_cairo_set_source_window(cr, window, 0, 0);

        cairo_paint(cr);

        cairo_destroy(cr);

    }

    /* Sauvegarde de l'éventuelle position */

    if (GTK_IS_SCROLLED_WINDOW(content))
    {
        adj = gtk_scrolled_window_get_hadjustment(GTK_SCROLLED_WINDOW(content));
        item->hadj_value = gtk_adjustment_get_value(adj);

        adj = gtk_scrolled_window_get_vadjustment(GTK_SCROLLED_WINDOW(content));
        item->vadj_value = gtk_adjustment_get_value(adj);

    }

    /* Opération de basculement effectif */

    stack = GTK_STACK(gtk_builder_get_object(builder, "stack"));

    mask = GTK_WIDGET(gtk_builder_get_object(builder, "mask"));

    gtk_spinner_start(GTK_SPINNER(mask));

    if (item->surface != NULL)
        g_signal_connect(mask, "draw", G_CALLBACK(g_panel_item_draw_mask), item);

    gtk_stack_set_visible_child(stack, mask);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau après sa mise à jour.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_panel_item_switch_to_updated_content(GPanelItem *item)
{
    GtkBuilder *builder;                    /* Constructeur sous-jacent    */
    GtkWidget *content;                     /* Composant à faire évoluer   */
    GtkAdjustment *adj;                     /* Défilement éventuel         */
    GtkStack *stack;                        /* Pile de composants GTK      */
    GtkWidget *mask;                        /* Masque des travaux          */

    if (g_atomic_int_get(&item->switched) > 1)
        goto skip;

    /* Restauration d'une éventuelle position */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(item->widget));

    content = GTK_WIDGET(gtk_builder_get_object(builder, "content"));

    if (GTK_IS_SCROLLED_WINDOW(content))
    {
        adj = gtk_scrolled_window_get_hadjustment(GTK_SCROLLED_WINDOW(content));
        gtk_adjustment_set_value(adj, item->hadj_value);

        adj = gtk_scrolled_window_get_vadjustment(GTK_SCROLLED_WINDOW(content));
        gtk_adjustment_set_value(adj, item->vadj_value);

    }

    /* Opération de basculement effectif */

    stack = GTK_STACK(gtk_builder_get_object(builder, "stack"));

    gtk_stack_set_visible_child(stack, content);

    mask = GTK_WIDGET(gtk_builder_get_object(builder, "mask"));

    g_signal_handlers_disconnect_by_func(mask, G_CALLBACK(g_panel_item_draw_mask), item);

    gtk_spinner_stop(GTK_SPINNER(mask));

    /* Supression de la copie d'affichage */

    if (item->surface != NULL)
    {
        cairo_surface_destroy(item->surface);
        item->surface = NULL;
    }

    g_object_unref(G_OBJECT(builder));

 skip:

    g_atomic_int_dec_and_test(&item->switched);

}
