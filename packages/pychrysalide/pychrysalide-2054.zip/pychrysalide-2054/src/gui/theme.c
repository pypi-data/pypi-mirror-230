
/* Chrysalide - Outil d'analyse de fichiers binaires
 * theme.c - gestion d'un thème pour l'interface grahique
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


#include "theme.h"


#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <gio/gio.h>


#include "core/theme.h"
#include "../common/xml.h"
#include "../plugins/pglist.h"



/* Thème graphique pour l'éditeur (instance) */
struct _GEditorTheme
{
    GObject parent;                         /* A laisser en premier        */

    GResource *resource;                    /* Resources GLib associées    */

    char *name;                             /* Désignation courte du thème */

    xmlDocPtr xdoc;                         /* Document XML récupéré       */
    xmlXPathContextPtr context;             /* Contexte d'analyse associé  */

    GtkCssProvider **providers;             /* Fournisseur CSS appliqués   */
    size_t count;                           /* Quantité de ces fournisseurs*/

};


/* Thème graphique pour l'éditeur (classe) */
struct _GEditorThemeClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des éléments réactifs de l'éditeur. */
static void g_editor_theme_class_init(GEditorThemeClass *);

/* Initialise une instance d'élément réactif pour l'éditeur. */
static void g_editor_theme_init(GEditorTheme *);

/* Supprime toutes les références externes. */
static void g_editor_theme_dispose(GEditorTheme *);

/* Procède à la libération totale de la mémoire. */
static void g_editor_theme_finalize(GEditorTheme *);

/* Active une partie choisie de thème graphique. */
static void g_editor_theme_load_section(GEditorTheme *, GdkScreen *, gboolean, const char *);



/* Indique le type défini pour un theme de l'interface graphique. */
G_DEFINE_TYPE(GEditorTheme, g_editor_theme, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des éléments réactifs de l'éditeur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_theme_class_init(GEditorThemeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_editor_theme_dispose;
    object->finalize = (GObjectFinalizeFunc)g_editor_theme_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : theme = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'élément réactif pour l'éditeur.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_theme_init(GEditorTheme *theme)
{
    theme->resource = NULL;

    theme->name = NULL;

    theme->xdoc = NULL;
    theme->context = NULL;

    theme->providers = NULL;
    theme->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : theme = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_theme_dispose(GEditorTheme *theme)
{
    if (theme->resource != NULL)
    {
        g_resource_unref(theme->resource);
        theme->resource = NULL;
    }

    G_OBJECT_CLASS(g_editor_theme_parent_class)->dispose(G_OBJECT(theme));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : theme = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_theme_finalize(GEditorTheme *theme)
{
    if (theme->name != NULL)
        free(theme->name);

    if (theme->xdoc != NULL)
        close_xml_file(theme->xdoc, theme->context);

    G_OBJECT_CLASS(g_editor_theme_parent_class)->finalize(G_OBJECT(theme));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin d'accès vers un ressource.                 *
*                include  = enregistre la ressource dans l'espace global ?    *
*                                                                             *
*  Description : Charge les éléments associés à un thème graphique.           *
*                                                                             *
*  Retour      : Adresse de la représentation ou NULL en cas d'échec.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEditorTheme *g_editor_theme_new(const char *filename, bool include)
{
    GEditorTheme *result;                   /* Adresse à retourner         */
    GResource *resource;                    /* Resources du thème          */
    char **children;                        /* Sous-éléments présents      */
    size_t name_len;                        /* Taille de la désignation    */
    char *name;                             /* Désignation courte du thème */
    char *path;                             /* Chemin vers à la définition */
    GBytes *bytes;                          /* Données d'identité          */
    const char *data;                       /* Données XML de définition   */
    size_t data_len;                        /* Quantité de ces données     */
    xmlDocPtr xdoc;                         /* Document XML récupéré       */
    xmlXPathContextPtr context;             /* Contexte d'analyse associé  */
    bool status;                            /* Bilan de chargement         */

    /* Ouverture de la ressource */

    resource = g_resource_load(filename, NULL);
    if (resource == NULL) goto bad_res;

    children = g_resource_enumerate_children(resource, "/org/chrysalide/gui/themes",
                                             G_RESOURCE_LOOKUP_FLAGS_NONE, NULL);

    if (children == NULL || children[0] == NULL)
        goto empty_res;

    name_len = strlen(children[0]);

    if (name_len < 2 || children[0][name_len - 1] != '/')
        goto empty_res;

    name = strndup(children[0], name_len - 1);

    /* Chargement de la définition XML */

    asprintf(&path, "/org/chrysalide/gui/themes/%s/definition.xml", name);

    bytes = g_resource_lookup_data(resource, path, G_RESOURCE_LOOKUP_FLAGS_NONE, NULL);

    free(path);

    if (bytes == NULL)
        goto no_def;

    data = g_bytes_get_data(bytes, &data_len);

    status = load_xml_from_memory(data, data_len, &xdoc, &context);

    g_bytes_unref(bytes);

    if (!status)
        goto bad_xml;

    /* Création du thème */

    result = g_object_new(G_TYPE_EDITOR_THEME, NULL);

    result->resource = resource;

    result->name = name;

    result->xdoc = xdoc;
    result->context = context;

    if (include)
        g_resources_register(result->resource);

    return result;

 bad_xml:

 no_def:

    free(name);

 empty_res:

    g_resource_unref(resource);

 bad_res:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : theme = theme graphique à consulter.                         *
*                                                                             *
*  Description : Indique le nom d'un thème donné.                             *
*                                                                             *
*  Retour      : Désignation courte associée au thème.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_editor_theme_get_name(const GEditorTheme *theme)
{
    const char *result;                     /* Désignation à retourner     */

    result = theme->name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : theme   = theme graphique à charger.                         *
*                screen  = écran visé par le chargement d'un thème.           *
*                dark    = indique une préférence pour la variante foncée.    *
*                section = sous-partie de la définition à traiter.            *
*                                                                             *
*  Description : Active une partie choisie de thème graphique.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_theme_load_section(GEditorTheme *theme, GdkScreen *screen, gboolean dark, const char *section)
{
    char *def_prefix;                       /* Base de ressource par défaut*/
    char *sec_access;                       /* Chemin d'accès à la section */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    unsigned int i;                         /* Boucle de parcours          */
    char *access;                           /* Chemin d'accès à un élément */
    char *value;                            /* Resource à charger          */
    char *path;                             /* Chemin d'accès final        */
    GtkCssProvider *provider;               /* Nouveau fournisseur CSS     */

    asprintf(&def_prefix, "/org/chrysalide/gui/themes/%s/", theme->name);

    asprintf(&sec_access, "/ChrysalideTheme/resources/%s/path", section);

    xobject = get_node_xpath_object(theme->context, sec_access);

    for (i = 0; i < XPATH_OBJ_NODES_COUNT(xobject); i++)
    {
        asprintf(&access, "%s[position()=%u]", sec_access, i + 1);

        value = get_node_text_value(theme->context, access);

        free(access);

        if (strlen(value) > 0)
        {
            if (value[0] == '/')
                asprintf(&path, "resource://%s", value);
            else
                asprintf(&path, "resource://%s%s", def_prefix, value);

            provider = load_css_content(screen, path);

            if (provider != NULL)
            {
                theme->providers = realloc(theme->providers, ++theme->count * sizeof(GtkCssProvider *));
                theme->providers[theme->count - 1] = provider;
            }

        }

        free(value);

    }

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    free(sec_access);

    free(def_prefix);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : theme  = theme graphique à charger.                          *
*                screen = écran visé par le chargement d'un thème.            *
*                dark   = indique une préférence pour la variante foncée.     *
*                                                                             *
*  Description : Active un thème graphique particulier.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_theme_load(GEditorTheme *theme, GdkScreen *screen, gboolean dark)
{
    char **resources;                       /* Fichiers supplémentaires    */
    size_t count;                           /* Nombre de ces fichiers      */
    size_t i;                               /* Boucle de parcours          */
    GtkCssProvider *provider;               /* Nouveau fournisseur CSS     */

    /* Chargement du thème global courant */

    g_editor_theme_load_section(theme, screen, dark, "common");

    if (dark)
        g_editor_theme_load_section(theme, screen, dark, "dark");
    else
        g_editor_theme_load_section(theme, screen, dark, "light");

    /* Chargement des thèmes des greffons */

    resources = NULL;
    count = 0;

    include_plugin_theme(dark, &resources, &count);

    for (i = 0; i < count; i++)
    {
        provider = load_css_content(screen, resources[i]);

        if (provider != NULL)
        {
            theme->providers = realloc(theme->providers, ++theme->count * sizeof(GtkCssProvider *));
            theme->providers[theme->count - 1] = provider;
        }

        free(resources[i]);

    }

    if (resources != NULL)
        free(resources);

}
