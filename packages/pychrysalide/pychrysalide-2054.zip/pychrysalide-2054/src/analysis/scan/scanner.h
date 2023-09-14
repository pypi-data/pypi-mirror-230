
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scanner.h - prototypes pour le parcours de contenus à la recherche de motifs
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


#ifndef _ANALYSIS_SCAN_SCANNER_H
#define _ANALYSIS_SCAN_SCANNER_H


#include <glib-object.h>


#include "context.h"
#include "expr.h"
#include "options.h"
#include "rule.h"
#include "../../common/szstr.h"



#define G_TYPE_CONTENT_SCANNER            g_content_scanner_get_type()
#define G_CONTENT_SCANNER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CONTENT_SCANNER, GContentScanner))
#define G_IS_CONTENT_SCANNER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CONTENT_SCANNER))
#define G_CONTENT_SCANNER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CONTENT_SCANNER, GContentScannerClass))
#define G_IS_CONTENT_SCANNER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CONTENT_SCANNER))
#define G_CONTENT_SCANNER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CONTENT_SCANNER, GContentScannerClass))


/* Encadrement d'une recherche au sein de contenus binaires (instance) */
typedef struct _GContentScanner GContentScanner;

/* Encadrement d'une recherche au sein de contenus binaires (classe) */
typedef struct _GContentScannerClass GContentScannerClass;


/* Indique le type défini pour une recherche dans du binaire. */
GType g_content_scanner_get_type(void);

/* Prépare une recherche de motifs dans du contenu binaire. */
GContentScanner *g_content_scanner_new_from_text(const char *);

/* Prépare une recherche de motifs dans du contenu binaire. */
GContentScanner *g_content_scanner_new_from_file(const char *);

/* Indique le chemin d'un éventuel fichier de source. */
const char *g_content_scanner_get_filename(const GContentScanner *);

/* Inclut les définitions d'un fichier de règles externe. */
bool g_content_scanner_include_resource(GContentScanner *, const char *);

/* Intègre une nouvelle règle de détection. */
bool g_content_scanner_add_rule(GContentScanner *, GScanRule *);

/* Définit l'expression d'une correspondance recherchée. */
GScanContext *g_content_scanner_analyze(GContentScanner *, GScanOptions *, GBinContent *);

/* Affiche un gestionnaire de recherches au format texte. */
void g_content_scanner_output_to_text(const GContentScanner *, GScanContext *, bool, int);

/* Convertit un gestionnaire de recherches en texte. */
char *g_content_scanner_convert_to_text(const GContentScanner *, GScanContext *);

/* Affiche un gestionnaire de recherches au format JSON. */
void g_content_scanner_output_to_json(const GContentScanner *, GScanContext *, const sized_string_t *, unsigned int, int);

/* Convertit un gestionnaire de recherches en JSON. */
char *g_content_scanner_convert_to_json(const GContentScanner *, GScanContext *);



#endif  /* _ANALYSIS_SCAN_SCANNER_H */
