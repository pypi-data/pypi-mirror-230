
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cdb.h - prototypes pour la manipulation des archives au format CDB
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_CDB_H
#define _ANALYSIS_DB_CDB_H


#include <glib-object.h>
#include <stdbool.h>
#include <openssl/ssl.h>


#include "protocol.h"
#include "misc/rlestr.h"



#define G_TYPE_CDB_ARCHIVE            g_cdb_archive_get_type()
#define G_CDB_ARCHIVE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CDB_ARCHIVE, GCdbArchive))
#define G_IS_CDB_ARCHIVE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CDB_ARCHIVE))
#define G_CDB_ARCHIVE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CDB_ARCHIVE, GCdbArchiveClass))
#define G_IS_CDB_ARCHIVE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CDB_ARCHIVE))
#define G_CDB_ARCHIVE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CDB_ARCHIVE, GCdbArchiveClass))


/* Description d'une archive d'éléments utilisateur (instance) */
typedef struct _GCdbArchive GCdbArchive;

/* Description d'une archive d'éléments utilisateur (classe) */
typedef struct _GCdbArchiveClass GCdbArchiveClass;


/* Indique le type défini pour une une archive d'éléments utilisateur. */
GType g_cdb_archive_get_type(void);

/* Prépare un client pour une connexion à une BD. */
GCdbArchive *g_cdb_archive_new(const char *, const char *, const rle_string *, const rle_string *, DBError *);

/* Construit un chemin pour un fichier propre à l'archive. */
char *g_cdb_archive_get_tmp_filename(const GCdbArchive *, const char *);

/* Enregistre une archive avec tous les éléments à conserver. */
DBError g_cdb_archive_write(const GCdbArchive *);

/* Détermine l'archive correspond à une cible recherchée. */
bool g_cdb_archive_compare_is_suitable_for(const GCdbArchive *, const rle_string *, const rle_string *);



#endif  /* _ANALYSIS_DB_CDB_H */
