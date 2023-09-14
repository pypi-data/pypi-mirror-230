
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loaded-int.h - définitions internes propres aux contenus chargés
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


#ifndef _ANALYSIS_LOADED_INT_H
#define _ANALYSIS_LOADED_INT_H


#include "loaded.h"
#include "../glibext/delayed-int.h"



/* Interprète un contenu chargé avec un appui XML. */
typedef bool (* restore_content_fc) (GLoadedContent *, xmlDoc *, xmlXPathContext *, const char *);

/* Ecrit une sauvegarde de l'élément dans un fichier XML. */
typedef bool (* save_content_fc) (GLoadedContent *, xmlDoc *, xmlXPathContext *, const char *);

/* Fournit le contenu représenté de l'élément chargé. */
typedef GBinContent * (* get_content_fc) (const GLoadedContent *);

/* Décrit la nature du contenu reconnu pour l'élément chargé. */
typedef char * (* get_content_class_fc) (const GLoadedContent *, bool);

/* Assure l'analyse d'un contenu chargé en différé. */
typedef bool (* analyze_loaded_fc) (GLoadedContent *, bool, bool, wgroup_id_t, GtkStatusStack *);

/* Fournit le désignation associée à l'élément chargé. */
typedef char * (* describe_loaded_fc) (const GLoadedContent *, bool);

#ifdef INCLUDE_GTK_SUPPORT

/* Détermine le nombre de vues disponibles pour un contenu. */
typedef unsigned int (* count_loaded_views_fc) (const GLoadedContent *);

/* Fournit le nom d'une vue donnée d'un contenu chargé. */
typedef char * (* get_loaded_view_name_fc) (const GLoadedContent *, unsigned int);

/* Met en place la vue initiale pour un contenu chargé. */
typedef GtkWidget * (* build_loaded_def_view_fc) (GLoadedContent *);

/* Met en place la vue demandée pour un contenu chargé. */
typedef GtkWidget * (* build_loaded_view_fc) (GLoadedContent *, unsigned int);

/* Retrouve l'indice correspondant à la vue donnée d'un contenu. */
typedef unsigned int (* get_loaded_view_index_fc) (GLoadedContent *, GtkWidget *);

/* Fournit toutes les options d'affichage pour un contenu. */
typedef GDisplayOptions * (* get_loaded_options_fc) (const GLoadedContent *, unsigned int);

#endif


/* Accès à un contenu binaire quelconque (instance) */
struct _GLoadedContent
{
    GObject parent;                         /* A laisser en premier        */

};

/* Accès à un contenu binaire quelconque (classe) */
struct _GLoadedContentClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Méthodes virtuelles */

    restore_content_fc restore;             /* Restauration depuis du XML  */
    save_content_fc save;                   /* Sauvegarde dans du XML      */

    get_content_fc get_content;             /* Fourniture du contenu brut  */
    get_content_class_fc get_content_class; /* Indication de classe liée   */

    analyze_loaded_fc analyze;              /* Analyse du contenu chargé   */

    describe_loaded_fc describe;            /* Description de contenu      */

#ifdef INCLUDE_GTK_SUPPORT

    count_loaded_views_fc count_views;      /* Compteur de vues            */
    get_loaded_view_name_fc get_view_name;  /* Désignation d'une vue donnée*/
    build_loaded_def_view_fc build_def_view;/* Mise en place initiale      */
    build_loaded_view_fc build_view;        /* Mise en place de vues       */
    get_loaded_view_index_fc get_view_index;/* Récupération d'indice de vue*/

    get_loaded_options_fc get_options;      /* Obtention de liste d'options*/

#endif

    /* Signaux */

    void (* analyzed) (GLoadedContent *, gboolean);

};



#endif  /* _ANALYSIS_LOADED_INT_H */
