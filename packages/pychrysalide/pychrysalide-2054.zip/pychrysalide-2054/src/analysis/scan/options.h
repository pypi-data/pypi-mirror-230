
/* Chrysalide - Outil d'analyse de fichiers binaires
 * options.h - prototypes pour le rassemblement des options d'analyse communiquées par le donneur d'ordre
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_OPTIONS_H
#define _ANALYSIS_SCAN_OPTIONS_H


#include <glib-object.h>
#include <stdbool.h>



#define G_TYPE_SCAN_OPTIONS            g_scan_options_get_type()
#define G_SCAN_OPTIONS(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_OPTIONS, GScanOptions))
#define G_IS_SCAN_OPTIONS(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_OPTIONS))
#define G_SCAN_OPTIONS_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_OPTIONS, GScanOptionsClass))
#define G_IS_SCAN_OPTIONS_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_OPTIONS))
#define G_SCAN_OPTIONS_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_OPTIONS, GScanOptionsClass))


/* Rassemblement d'options d'analyses (instance) */
typedef struct _GScanOptions GScanOptions;

/* Rassemblement d'options d'analyses (classe) */
typedef struct _GScanOptionsClass GScanOptionsClass;


/* Indique le type défini pour un ensemble d'options d'analyses. */
GType g_scan_options_get_type(void);

/* Crée un réceptacle pour diverses options d'analyse. */
GScanOptions *g_scan_options_new(void);

/* Indique le type d'un moteur d'analyse de données sélectionné. */
GType g_scan_options_get_backend_for_data(const GScanOptions *);

/* Sélectionne un type de moteur d'analyse pour données brutes. */
void g_scan_options_set_backend_for_data(GScanOptions *, GType);

/* Impose le format JSON comme type de sortie. */
bool g_scan_options_get_print_json(const GScanOptions *);

/* Mémorise le format JSON comme type de sortie. */
void g_scan_options_set_print_json(GScanOptions *, bool);

/* Indique un besoin d'affichage des correspondances finales. */
bool g_scan_options_get_print_strings(const GScanOptions *);

/* Mémorise un besoin d'affichage des correspondances finales. */
void g_scan_options_set_print_strings(GScanOptions *, bool);

/* Indique un besoin de statistiques en fin de compilation. */
bool g_scan_options_get_print_stats(const GScanOptions *);

/* Mémorise un besoin de statistiques en fin de compilation. */
void g_scan_options_set_print_stats(GScanOptions *, bool);



#endif  /* _ANALYSIS_SCAN_OPTIONS_H */
