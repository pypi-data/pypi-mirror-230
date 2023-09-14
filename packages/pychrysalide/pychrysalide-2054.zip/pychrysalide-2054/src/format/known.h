
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.h - prototypes pour le support des différents formats binaires reconnus
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _FORMAT_KNOWN_H
#define _FORMAT_KNOWN_H


#include <glib-object.h>
#include <stdbool.h>


#include "../analysis/content.h"
#include "../glibext/delayed.h"
#include "../glibext/notifier.h"



#define G_TYPE_KNOWN_FORMAT            g_known_format_get_type()
#define G_KNOWN_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KNOWN_FORMAT, GKnownFormat))
#define G_IS_KNOWN_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KNOWN_FORMAT))
#define G_KNOWN_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KNOWN_FORMAT, GKnownFormatClass))
#define G_IS_KNOWN_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KNOWN_FORMAT))
#define G_KNOWN_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KNOWN_FORMAT, GKnownFormatClass))


/* Format binaire générique (instance) */
typedef struct _GKnownFormat GKnownFormat;

/* Format binaire générique (classe) */
typedef struct _GKnownFormatClass GKnownFormatClass;


/* Indique le type défini pour un format binaire générique. */
GType g_known_format_get_type(void);

/* Définit le contenu binaire à analyser. */
void g_known_format_set_content(GKnownFormat *, GBinContent *);

/* Fournit une référence vers le contenu binaire analysé. */
GBinContent *g_known_format_get_content(const GKnownFormat *);

/* Indique la désignation interne du format. */
char *g_known_format_get_key(const GKnownFormat *);

/* Fournit une description humaine du format. */
char *g_known_format_get_description(const GKnownFormat *);

/* Assure l'interprétation d'un format en différé. */
bool g_known_format_analyze(GKnownFormat *, wgroup_id_t, GtkStatusStack *);

/* Réalise un traitement post-désassemblage. */
void g_known_format_complete_analysis(GKnownFormat *, wgroup_id_t, GtkStatusStack *);



#endif  /* _FORMAT_KNOWN_H */
