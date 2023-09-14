
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.h - prototypes pour le support du format ELF
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ELF_FORMAT_H
#define _PLUGINS_ELF_FORMAT_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>
#include <format/executable.h>


#include "elf_def.h"



#define G_TYPE_ELF_FORMAT            g_elf_format_get_type()
#define G_ELF_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ELF_FORMAT, GElfFormat))
#define G_IS_ELF_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ELF_FORMAT))
#define G_ELF_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ELF_FORMAT, GElfFormatClass))
#define G_IS_ELF_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ELF_FORMAT))
#define G_ELF_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ELF_FORMAT, GElfFormatClass))


/* Format d'exécutable ELF (instance) */
typedef struct _GElfFormat GElfFormat;

/* Format d'exécutable ELF (classe) */
typedef struct _GElfFormatClass GElfFormatClass;


/* Valide un contenu comme étant un format Elf. */
bool check_elf_format(const GBinContent *);

/* Indique le type défini pour un format d'exécutable ELF. */
GType g_elf_format_get_type(void);

/* Prend en charge un nouveau format ELF. */
GExeFormat *g_elf_format_new(GBinContent *);

/* Présente l'en-tête ELF du format chargé. */
const elf_header *g_elf_format_get_header(const GElfFormat *);



#endif  /* _PLUGINS_ELF_FORMAT_H */
