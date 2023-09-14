
/* Chrysalide - Outil d'analyse de fichiers binaires
 * file.h - prototypes pour le chargement de données binaires à partir d'un fichier
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


#ifndef _ANALYSIS_CONTENTS_FILE_H
#define _ANALYSIS_CONTENTS_FILE_H


#include <glib-object.h>


#include "../content.h"



#define G_TYPE_FILE_CONTENT            (g_file_content_get_type())
#define G_FILE_CONTENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_FILE_CONTENT, GFileContent))
#define G_IS_FILE_CONTENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_FILE_CONTENT))
#define G_FILE_CONTENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_FILE_CONTENT, GFileContentClass))
#define G_IS_FILE_CONTENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_FILE_CONTENT))
#define G_FILE_CONTENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_FILE_CONTENT, GFileContentClass))


/* Contenu de données binaires issues d'un fichier (instance) */
typedef struct _GFileContent GFileContent;

/* Contenu de données binaires issues d'un fichier (classe) */
typedef struct _GFileContentClass GFileContentClass;


/* Indique le type défini par la GLib pour les contenus de données. */
GType g_file_content_get_type(void);

/* Charge en mémoire le contenu d'un fichier donné. */
GBinContent *g_file_content_new(const char *);

/* Fournit le nom de fichier associé au contenu binaire. */
const char *g_file_content_get_filename(const GFileContent *);



#endif  /* _ANALYSIS_CONTENTS_FILE_H */
