
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pe-int.h - prototypes pour les structures internes du format Portable Executable
 *
 * Copyright (C) 2009-2017 Cyrille Bagard
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


#ifndef _PLUGINS_PE_PE_INT_H
#define _PLUGINS_PE_PE_INT_H


#include <format/executable-int.h>


#include "pe_def.h"
#include "format.h"



/* Format d'exécutable PE (instance) */
struct _GPeFormat
{
    GExeFormat parent;                      /* A laisser en premier        */

    image_dos_header dos_header;            /* En-tête DOS                 */
    mrange_t rich_header;                   /* En-tête enrichi             */
    image_nt_headers nt_headers;            /* En-tête Windows             */

    image_section_header *sections;         /* Liste des sections          */

    bool loaded;                            /* Détection partielle menée   */

};

/* Format d'exécutable PE (classe) */
struct _GPeFormatClass
{
    GExeFormatClass parent;                 /* A laisser en premier        */

};


/* Procède à la lecture d'un en-tête de programme DOS. */
bool read_dos_image_header(const GPeFormat *, image_dos_header *);

/* Procède à la lecture d'un en-tête de programme PE (1). */
bool read_pe_file_header(const GPeFormat *, vmpa2t *, image_file_header *);

/* Procède à la lecture d'un en-tête de programme PE (2). */
bool read_pe_optional_header(const GPeFormat *, vmpa2t *, image_optional_header *);

/* Procède à la lecture d'un en-tête de programme PE. */
bool read_pe_nt_header(const GPeFormat *, image_nt_headers *, vmpa2t *);

/* Procède à la lecture d'un en-tête de section PE. */
bool read_pe_image_section_header(const GPeFormat *, vmpa2t *, image_section_header *);

/* Procède à la lecture d'un répertoire d'exportations. */
bool read_pe_image_export_directory(const GPeFormat *, vmpa2t *, image_export_directory *);

/* Procède à la lecture d'un répertoire de programme PE. */
bool read_pe_image_import_descriptor(const GPeFormat *, vmpa2t *, image_import_descriptor *);



#endif  /* _PLUGINS_PE_PE_INT_H */
