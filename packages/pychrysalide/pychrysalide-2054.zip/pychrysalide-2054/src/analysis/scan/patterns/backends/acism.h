
/* Chrysalide - Outil d'analyse de fichiers binaires
 * acism.h - prototypes pour la méthode de recherche basée sur l'algorithme Aho-Corasick Interleaved State-transition Matrix
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


#ifndef _ANALYSIS_SCAN_PATTERNS_BACKENDS_ACISM_H
#define _ANALYSIS_SCAN_PATTERNS_BACKENDS_ACISM_H


#include <glib-object.h>
#include <stdbool.h>


#include "../backend.h"



#define G_TYPE_ACISM_BACKEND            g_acism_backend_get_type()
#define G_ACISM_BACKEND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ACISM_BACKEND, GAcismBackend))
#define G_IS_ACISM_BACKEND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ACISM_BACKEND))
#define G_ACISM_BACKEND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ACISM_BACKEND, GAcismBackendClass))
#define G_IS_ACISM_BACKEND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ACISM_BACKEND))
#define G_ACISM_BACKEND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ACISM_BACKEND, GAcismBackendClass))


/* Méthode de recherche basée sur l'algorithme Acism (instance) */
typedef struct _GAcismBackend GAcismBackend;

/* Méthode de recherche basée sur l'algorithme Acism (classe) */
typedef struct _GAcismBackendClass GAcismBackendClass;


/* Indique le type défini pour un moteur de recherche pour données. */
GType g_acism_backend_get_type(void);

/* Crée une méthode de recherche basée sur l'algorithme Acism. */
GEngineBackend *g_acism_backend_new(void);



#endif  /* _ANALYSIS_SCAN_PATTERNS_BACKENDS_ACISM_H */
