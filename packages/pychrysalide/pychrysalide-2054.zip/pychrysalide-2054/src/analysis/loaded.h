
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loaded.h - prototypes pour l'intégration des contenus chargés
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_LOADED_H
#define _ANALYSIS_LOADED_H


#include <glib-object.h>
#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include "content.h"
#include "../common/xml.h"
#include "../glibext/gdisplayoptions.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../gtkext/gtkdockstation.h"
#endif



/* ---------------------- GESTION SOUS FORME DE CONTENU CHARGE ---------------------- */


#define G_TYPE_LOADED_CONTENT            g_loaded_content_get_type()
#define G_LOADED_CONTENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LOADED_CONTENT, GLoadedContent))
#define G_IS_LOADED_CONTENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LOADED_CONTENT))
#define G_LOADED_CONTENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_LOADED_CONTENT, GLoadedContentClass))
#define G_IS_LOADED_CONTENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_LOADED_CONTENT))
#define G_LOADED_CONTENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_LOADED_CONTENT, GLoadedContentClass))


/* Accès à un contenu binaire quelconque (instance) */
typedef struct _GLoadedContent GLoadedContent;

/* Accès à un contenu binaire quelconque (instance) */
typedef struct _GLoadedContentClass GLoadedContentClass;


/* Détermine le type d'une interface pour l'intégration de contenu chargé. */
GType g_loaded_content_get_type(void) G_GNUC_CONST;

/* Interprète un contenu chargé avec un appui XML. */
bool g_loaded_content_restore(GLoadedContent *, xmlDoc *, xmlXPathContext *, const char *);

/* Ecrit une sauvegarde de l'élément dans un fichier XML. */
bool g_loaded_content_save(GLoadedContent *, xmlDoc *, xmlXPathContext *, const char *);

/* Fournit le contenu représenté de l'élément chargé. */
GBinContent *g_loaded_content_get_content(const GLoadedContent *);

/* Décrit la nature du contenu reconnu pour l'élément chargé. */
char *g_loaded_content_get_content_class(const GLoadedContent *, bool);

/* Lance l'analyse propre à l'élément chargé. */
void g_loaded_content_analyze(GLoadedContent *, bool, bool);

/* Lance l'analyse de l'élément chargé et attend sa conclusion. */
bool g_loaded_content_analyze_and_wait(GLoadedContent *, bool, bool);

/* Fournit le désignation associée à l'élément chargé. */
char *g_loaded_content_describe(const GLoadedContent *, bool);

/* Etablit une liste d'obscurcissements présents. */
char **g_loaded_content_detect_obfuscators(const GLoadedContent *, bool, size_t *);



/* --------------------------- GESTION DYNAMIQUE DES VUES --------------------------- */


#ifdef INCLUDE_GTK_SUPPORT

/* Détermine le nombre de vues disponibles pour un contenu. */
unsigned int g_loaded_content_count_views(const GLoadedContent *);

/* Fournit le nom d'une vue donnée d'un contenu chargé. */
char *g_loaded_content_get_view_name(const GLoadedContent *, unsigned int);

/* Met en place la vue initiale pour un contenu chargé. */
GtkWidget *g_loaded_content_build_default_view(GLoadedContent *);

/* Met en place la vue demandée pour un contenu chargé. */
GtkWidget *g_loaded_content_build_view(GLoadedContent *, unsigned int);

/* Retrouve l'indice correspondant à la vue donnée d'un contenu. */
unsigned int g_loaded_content_get_view_index(GLoadedContent *, GtkWidget *);

/* Fournit toutes les options d'affichage pour un contenu. */
GDisplayOptions *g_loaded_content_get_display_options(const GLoadedContent *, unsigned int);

#endif



/* ----------------------- VUES ET BASCULEMENT ENTRE LES VUES ----------------------- */


#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la station d'accueil d'un panneau d'affichage. */
GtkDockStation *get_dock_station_for_view_panel(GtkWidget *);

/* Fournit le support défilant d'un panneau d'affichage. */
GtkWidget *get_scroll_window_for_view_panel(GtkWidget *);

/* Fournit le panneau chargé inclus dans un affichage. */
GtkWidget *get_loaded_panel_from_built_view(GtkWidget *);

#endif



#endif  /* _ANALYSIS_LOADED_H */
