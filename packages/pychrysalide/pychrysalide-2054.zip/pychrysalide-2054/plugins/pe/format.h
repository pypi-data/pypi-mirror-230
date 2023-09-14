
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pe.h - prototypes pour le support du format Portable Executable
 *
 * Copyright (C) 2010-2017 Cyrille Bagard
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


#ifndef _PLUGINS_PE_FORMAT_H
#define _PLUGINS_PE_FORMAT_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>
#include <format/executable.h>


#include "pe_def.h"



#define G_TYPE_PE_FORMAT            g_pe_format_get_type()
#define G_PE_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PE_FORMAT, GPeFormat))
#define G_IS_PE_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PE_FORMAT))
#define G_PE_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PE_FORMAT, GPeFormatClass))
#define G_IS_PE_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PE_FORMAT))
#define G_PE_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PE_FORMAT, GPeFormatClass))


/* Format d'exécutable PE (instance) */
typedef struct _GPeFormat GPeFormat;

/* Format d'exécutable PE (classe) */
typedef struct _GPeFormatClass GPeFormatClass;


/* Valide un contenu comme étant un format PE. */
bool check_pe_format(const GBinContent *);

/* Indique le type défini pour un format d'exécutable PE. */
GType g_pe_format_get_type(void);

/* Prend en charge un nouveau format PE. */
GExeFormat *g_pe_format_new(GBinContent *);

/* Présente l'en-tête MS-DOS du format chargé. */
const image_dos_header *g_pe_format_get_dos_header(const GPeFormat *);

/* Présente l'en-tête NT du format chargé. */
const image_nt_headers *g_pe_format_get_nt_headers(const GPeFormat *);

/* Indique si le format PE est en 32 bits ou en 64 bits. */
bool g_pe_format_get_is_32b(const GPeFormat *);

/* Offre un raccourci vers les répertoires du format PE. */
const image_data_directory *g_pe_format_get_directories(const GPeFormat *, size_t *);

/* Extrait le contenu d'un répertoire du format PE. */
void *g_pe_format_get_directory(const GPeFormat *, size_t);



#endif  /* _PLUGINS_PE_FORMAT_H */
