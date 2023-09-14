
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bitap.h - prototypes pour la méthode de recherche basée sur l'algorithme Bitap
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


#ifndef _ANALYSIS_SCAN_PATTERNS_BACKENDS_BITAP_H
#define _ANALYSIS_SCAN_PATTERNS_BACKENDS_BITAP_H


#include <glib-object.h>
#include <stdbool.h>


#include "../backend.h"



#define G_TYPE_BITAP_BACKEND            g_bitap_backend_get_type()
#define G_BITAP_BACKEND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BITAP_BACKEND, GBitapBackend))
#define G_IS_BITAP_BACKEND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BITAP_BACKEND))
#define G_BITAP_BACKEND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BITAP_BACKEND, GBitapBackendClass))
#define G_IS_BITAP_BACKEND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BITAP_BACKEND))
#define G_BITAP_BACKEND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BITAP_BACKEND, GBitapBackendClass))


/* Méthode de recherche basée sur l'algorithme Bitap (instance) */
typedef struct _GBitapBackend GBitapBackend;

/* Méthode de recherche basée sur l'algorithme Bitap (classe) */
typedef struct _GBitapBackendClass GBitapBackendClass;


/* Indique le type défini pour un moteur de recherche pour données. */
GType g_bitap_backend_get_type(void);

/* Crée une méthode de recherche basée sur l'algorithme Bitap. */
GEngineBackend *g_bitap_backend_new(void);



#endif  /* _ANALYSIS_SCAN_PATTERNS_BACKENDS_BITAP_H */
