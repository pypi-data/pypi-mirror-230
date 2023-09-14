
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.h - prototypes pour la reconnaissance de contenus binaires
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_LOADING_H
#define _ANALYSIS_LOADING_H


#include <glib-object.h>


#include "content.h"
#include "loaded.h"
#include "../glibext/delayed.h"



/* --------------------- EXPLORATION NON BLOQUANTE DES CONTENUS --------------------- */


#define G_TYPE_CONTENT_EXPLORER            g_content_explorer_get_type()
#define G_CONTENT_EXPLORER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CONTENT_EXPLORER, GContentExplorer))
#define G_IS_CONTENT_EXPLORER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CONTENT_EXPLORER))
#define G_CONTENT_EXPLORER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CONTENT_EXPLORER, GContentExplorerClass))
#define G_IS_CONTENT_EXPLORER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CONTENT_EXPLORER))
#define G_CONTENT_EXPLORER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CONTENT_EXPLORER, GContentExplorerClass))


/* Exploration de contenus binaires (instance) */
typedef struct _GContentExplorer GContentExplorer;

/* Exploration de contenus binaires (classe) */
typedef struct _GContentExplorerClass GContentExplorerClass;


/* Indique le type défini pour l'exploration de contenus binaires. */
GType g_content_explorer_get_type(void);

/* Crée un gestionnaire des explorations de contenus binaires. */
GContentExplorer *g_content_explorer_new(void);

/* Initie une nouvelle vague d'exploration de contenu. */
wgroup_id_t g_content_explorer_create_group(GContentExplorer *, GBinContent *);

/* Termine une vague d'exploration de contenu. */
void g_content_explorer_delete_group(GContentExplorer *, wgroup_id_t);

/* Ajoute un nouveau contenu découvert au crédit d'un groupe. */
void g_content_explorer_populate_group(GContentExplorer *, wgroup_id_t, GBinContent *);

/* Fournit la liste de tous les contenus disponibles. */
GBinContent **g_content_explorer_get_all(GContentExplorer *, wgroup_id_t, size_t *);



/* ------------------- RESOLUTION DE CONTENUS BINAIRES EN CHARGES ------------------- */


#define G_TYPE_CONTENT_RESOLVER            g_content_resolver_get_type()
#define G_CONTENT_RESOLVER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CONTENT_RESOLVER, GContentResolver))
#define G_IS_CONTENT_RESOLVER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CONTENT_RESOLVER))
#define G_CONTENT_RESOLVER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CONTENT_RESOLVER, GContentResolverClass))
#define G_IS_CONTENT_RESOLVER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CONTENT_RESOLVER))
#define G_CONTENT_RESOLVER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CONTENT_RESOLVER, GContentResolverClass))


/* Résolution de contenus binaires en formats chargés (instance) */
typedef struct _GContentResolver GContentResolver;

/* Résolution de contenus binaires en formats chargés (classe) */
typedef struct _GContentResolverClass GContentResolverClass;


/* Indique le type défini pour la résolution de contenus binaires en formats chargés. */
GType g_content_resolver_get_type(void);

/* Crée un gestionnaire des résolutions de contenus binaires. */
GContentResolver *g_content_resolver_new(void);

/* Initie une nouvelle vague de résolution de contenus. */
void g_content_resolver_create_group(GContentResolver *, wgroup_id_t, GBinContent **, size_t);

/* Termine une vague de résolution de contenu. */
void g_content_resolver_delete_group(GContentResolver *, wgroup_id_t);

/* Intègre un contenu chargé dans les résultats. */
void g_content_resolver_add_detected(GContentResolver *, wgroup_id_t, GLoadedContent *);

/* Fournit la liste de tous les contenus chargés valables. */
GLoadedContent **g_content_resolver_get_all(GContentResolver *, wgroup_id_t, size_t *);



#endif  /* _ANALYSIS_LOADING_H */
