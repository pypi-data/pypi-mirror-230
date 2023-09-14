
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scanner-int.h - prototypes internes pour le parcours de contenus à la recherche de motifs
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


#ifndef _ANALYSIS_SCAN_SCANNER_INT_H
#define _ANALYSIS_SCAN_SCANNER_INT_H


#include "scanner.h"


#include "patterns/backend.h"



/* Encadrement d'une recherche au sein de contenus binaires (instance) */
struct _GContentScanner
{
    GObject parent;                         /* A laisser en premier        */

    char *filename;                         /* Eventuel fichier d'origine  */

    GScanRule **rules;                      /* Règles de détection         */
    size_t rule_count;                      /* Nombre de ces règles        */

    GEngineBackend *data_backend;           /* Moteur pour les données     */

};

/* Encadrement d'une recherche au sein de contenus binaires (classe) */
struct _GContentScannerClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Met en place un scanner de contenus binaires. */
bool g_content_scanner_create_from_text(GContentScanner *, const char *);

/* Met en place un scanner de contenus binaires. */
bool g_content_scanner_create_from_file(GContentScanner *, const char *);



#endif  /* _ANALYSIS_SCAN_SCANNER_INT_H */
