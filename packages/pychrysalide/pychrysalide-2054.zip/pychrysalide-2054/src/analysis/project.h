
/* Chrysalide - Outil d'analyse de fichiers binaires
 * project.h - prototypes pour la gestion d'un groupe de fichiers binaires
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_PROJECT_H
#define _ANALYSIS_PROJECT_H


#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include "loaded.h"



#define PROJECT_XML_VERSION "2"



/* ------------------------- DEFINITION D'UN PROJET INTERNE ------------------------- */


#define G_TYPE_STUDY_PROJECT            g_study_project_get_type()
#define G_STUDY_PROJECT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_STUDY_PROJECT, GStudyProject))
#define G_IS_STUDY_PROJECT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_STUDY_PROJECT))
#define G_STUDY_PROJECT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_STUDY_PROJECT, GStudyProjectClass))
#define G_IS_STUDY_PROJECT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_STUDY_PROJECT))
#define G_STUDY_PROJECT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_STUDY_PROJECT, GStudyProjectClass))


/* Projet d'étude regroupant les binaires analysés (instance) */
typedef struct _GStudyProject GStudyProject;

/* Projet d'étude regroupant les binaires analysés  (classe) */
typedef struct _GStudyProjectClass GStudyProjectClass;


/* Indique le type défini pour un projet d'étude. */
GType g_study_project_get_type(void);

/* Crée un nouveau projet vierge. */
GStudyProject *g_study_project_new(void);

/* Crée un projet à partir du contenu XML d'un fichier. */
GStudyProject *g_study_project_open(const char *, bool);

/* Procède à l'enregistrement d'un projet donné. */
bool g_study_project_save(GStudyProject *, const char *);

/* Indique le chemin du fichier destiné à la sauvegarde. */
const char *g_study_project_get_filename(const GStudyProject *);



/* ------------------------ INTEGRATION DE CONTENUS BINAIRES ------------------------ */


/* Filtre sur les contenus chargeables */
typedef bool (* filter_loadable_cb) (GLoadedContent *, void *);

/* Assure l'intégration de contenus binaires dans un projet. */
void g_study_project_discover_binary_content(GStudyProject *, GBinContent *, bool, filter_loadable_cb, void *);

/* Réceptionne la recette d'une analyse de contenu. */
void on_loaded_content_analyzed(GLoadedContent *, gboolean, GStudyProject *);

#define g_study_project_lock_contents(p) \
    _g_study_project_lock_unlock_contents(p, true)

#define g_study_project_unlock_contents(p) \
    _g_study_project_lock_unlock_contents(p, false)

/* Verrouille ou déverrouille l'accès aux contenus chargés. */
void _g_study_project_lock_unlock_contents(GStudyProject *, bool);

/* Attache un contenu donné à un projet donné. */
void g_study_project_attach_content(GStudyProject *, GLoadedContent *);

/* Détache un contenu donné d'un projet donné. */
void g_study_project_detach_content(GStudyProject *, GLoadedContent *);

/* Dénombre les contenus associés à un projet. */
size_t _g_study_project_count_contents(GStudyProject *);

/* Dénombre les contenus associés à un projet. */
size_t g_study_project_count_contents(GStudyProject *);

/* Fournit l'ensemble des contenus associés à un projet. */
GLoadedContent **_g_study_project_get_contents(GStudyProject *, size_t *);

/* Fournit l'ensemble des contenus associés à un projet. */
GLoadedContent **g_study_project_get_contents(GStudyProject *, size_t *);



/* ------------------------- GESTION GLOBALISEE DES PROJETS ------------------------- */


#ifdef INCLUDE_GTK_SUPPORT

/* Fournit le gestionnaire des projets connus. */
GtkRecentManager *get_project_manager(void);

/* Place un projet au sommet de la pile des projets récents. */
void push_project_into_recent_list(const GStudyProject *);

#endif



#endif  /* _PROJECT_H */
