
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named.c - préparation de composants à l'affichage avec leurs noms
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "named.h"


#include <malloc.h>
#include <string.h>


#include "named-int.h"
#include "../glibext/named-int.h"



/* ---------------------- PREPARATION VIS A VIS DE L'EXTERIEUR ---------------------- */


/* Procède à l'initialisation de l'afficheur générique. */
static void gtk_built_named_widget_class_init(GtkBuiltNamedWidgetClass *);

/* Procède à l'initialisation d'une préparation pour affichage. */
static void gtk_built_named_widget_init(GtkBuiltNamedWidget *);

/* Procède à l'initialisation de l'interface de composant nommé. */
static void gtk_built_named_widget_named_interface_init(GNamedWidgetInterface *);

/* Supprime toutes les références externes. */
static void gtk_built_named_widget_dispose(GtkBuiltNamedWidget *);

/* Procède à la libération totale de la mémoire. */
static void gtk_built_named_widget_finalize(GtkBuiltNamedWidget *);



/* -------------------------- INTERFACE DE COMPOSANT NOMME -------------------------- */


/* Fournit le désignation associée à un composant nommé. */
static char *gtk_built_named_widget_get_name(const GtkBuiltNamedWidget *, bool);

/* Fournit le composant associé à un composant nommé. */
static GtkWidget *gtk_built_named_widget_get_widget(const GtkBuiltNamedWidget *);



/* ---------------------------------------------------------------------------------- */
/*                        PREPARATION VIS A VIS DE L'EXTERIEUR                        */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type des préparations de composant pour affichage avec noms. */
G_DEFINE_TYPE_WITH_CODE(GtkBuiltNamedWidget, gtk_built_named_widget, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_NAMED_WIDGET, gtk_built_named_widget_named_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur générique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_built_named_widget_class_init(GtkBuiltNamedWidgetClass *class)
{
    GObjectClass *object;                   /* Plus haut niveau équivalent */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_built_named_widget_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_built_named_widget_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation d'une préparation pour affichage. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_built_named_widget_init(GtkBuiltNamedWidget *widget)
{
    widget->builder = NULL;

    widget->name = NULL;
    widget->lname = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de composant nommé.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_built_named_widget_named_interface_init(GNamedWidgetInterface *iface)
{
    iface->get_name = (get_named_widget_name_fc)gtk_built_named_widget_get_name;
    iface->get_widget = (get_named_widget_widget_fc)gtk_built_named_widget_get_widget;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_built_named_widget_dispose(GtkBuiltNamedWidget *widget)
{
    g_clear_object(&widget->builder);

    G_OBJECT_CLASS(gtk_built_named_widget_parent_class)->dispose(G_OBJECT(widget));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_built_named_widget_finalize(GtkBuiltNamedWidget *widget)
{
    if (widget->name != NULL)
        free(widget->name);

    if (widget->lname != NULL)
        free(widget->lname);

    G_OBJECT_CLASS(gtk_built_named_widget_parent_class)->finalize(G_OBJECT(widget));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name  = nom associé à l'élément.                             *
*                lname = description longue du panneau.                       *
*                path  = chemin vers la description d'un composant graphique. *
*                                                                             *
*  Description : Crée une préparation pour l'affichage d'un composant nommé.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkBuiltNamedWidget *gtk_built_named_widget_new(const char *name, const char *lname, const char *path)
{
    GtkBuiltNamedWidget *result;            /* Instance à retourner        */

    result = g_object_new(GTK_TYPE_BUILT_NAMED_WIDGET, NULL);

    result->name = strdup(name);
    result->lname = strdup(lname);

    result->builder = gtk_builder_new_from_resource(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name  = nom associé à l'élément.                             *
*                lname = description longue du panneau.                       *
*                resid = indentificant d'une ressource pour un composant.     *
*                                                                             *
*  Description : Crée une préparation pour l'affichage d'un composant nommé.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkBuiltNamedWidget *gtk_built_named_widget_new_for_panel(const char *name, const char *lname, const char *resid)
{
    GtkBuiltNamedWidget *result;            /* Instance à retourner        */
    char *path;                             /* Chemin d'accès à constituer */

    asprintf(&path, "/org/chrysalide/gui/panels/%s.ui", resid);

    result = gtk_built_named_widget_new(name, lname, path);

    free(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = préparation de composant à consulter.               *
*                                                                             *
*  Description : Fournit le constructeur facilitant l'affichage.              *
*                                                                             *
*  Retour      : Constructeur mis en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkBuilder *gtk_built_named_widget_get_builder(const GtkBuiltNamedWidget *widget)
{
    GtkBuilder *result;                     /* Constructeur à retourner    */

    result = widget->builder;

    if (result)
        g_object_ref(G_OBJECT(result));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                            INTERFACE DE COMPOSANT NOMME                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant nommé à consulter.                        *
*                lname  = précise s'il s'agit d'une version longue ou non.    *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *gtk_built_named_widget_get_name(const GtkBuiltNamedWidget *widget, bool lname)
{
    char *result;                           /* Désignation à retourner     */

    if (lname)
        result = strdup(widget->lname);
    else
        result = strdup(widget->name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant nommé à consulter.                        *
*                                                                             *
*  Description : Fournit le composant associé à un composant nommé.           *
*                                                                             *
*  Retour      : Composant graphique GTK.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *gtk_built_named_widget_get_widget(const GtkBuiltNamedWidget *widget)
{
    GtkWidget *result;                      /* Composant GTK à renvoyer    */

    result = GTK_WIDGET(gtk_builder_get_object(widget->builder, "box"));

    g_object_ref(G_OBJECT(result));

    if (gtk_widget_get_parent(result))
        gtk_widget_unparent(result);

    return result;

}
