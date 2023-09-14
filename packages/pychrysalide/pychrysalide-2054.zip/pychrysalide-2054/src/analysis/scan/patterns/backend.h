
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend.h - prototypes pour une méthode de recherches au sein d'un contenu binaire
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_PATTERNS_BACKEND_H
#define _ANALYSIS_SCAN_PATTERNS_BACKEND_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>


#include "../context.h"
#include "../../content.h"



#define G_TYPE_ENGINE_BACKEND            g_engine_backend_get_type()
#define G_ENGINE_BACKEND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ENGINE_BACKEND, GEngineBackend))
#define G_IS_ENGINE_BACKEND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ENGINE_BACKEND))
#define G_ENGINE_BACKEND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ENGINE_BACKEND, GEngineBackendClass))
#define G_IS_ENGINE_BACKEND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ENGINE_BACKEND))
#define G_ENGINE_BACKEND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ENGINE_BACKEND, GEngineBackendClass))


/* Méthode de traitement d'un contenu binaire pour recherches (instance) */
typedef struct _GEngineBackend GEngineBackend;

/* Méthode de traitement d'un contenu binaire pour recherches (classe) */
typedef struct _GEngineBackendClass GEngineBackendClass;


/* Indique le type défini pour une méthode de recherche dans du binaire. */
GType g_engine_backend_get_type(void);

/* Indique la taille maximale des suites d'octets recherchées. */
size_t g_engine_backend_get_atom_max_size(const GEngineBackend *);

/* Inscrit dans le moteur une chaîne de caractères à rechercher. */
patid_t g_engine_backend_enroll_plain_pattern(GEngineBackend *, GScanContext *, const uint8_t *, size_t);

/* Met en ordre les derniers détails avant un premier scan. */
void g_engine_backend_warm_up(GEngineBackend *);

/* Parcours un contenu binaire à la recherche de motifs. */
void g_engine_backend_run_scan(const GEngineBackend *, GScanContext *);

/* Imprime quelques faits quant aux éléments mis en place. */
void g_engine_backend_output_stats(const GEngineBackend *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_BACKEND_H */
