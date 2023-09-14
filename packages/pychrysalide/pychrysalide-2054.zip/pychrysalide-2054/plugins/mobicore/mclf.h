
/* Chrysalide - Outil d'analyse de fichiers binaires
 * mclf.h - prototypes pour la prise en compte du format binaire 'MCLF'
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _PLUGINS_MOBICORE_MCLF_H
#define _PLUGINS_MOBICORE_MCLF_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>
#include <format/executable.h>



#define G_TYPE_MCLF_FORMAT                (g_mclf_format_get_type())
#define G_MCLF_FORMAT(obj)                (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_MCLF_FORMAT, GMCLFFormat))
#define G_IS_MCLF_FORMAT(obj)             (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_MCLF_FORMAT))
#define G_MCLF_FORMAT_CLASS(klass)        (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_MCLF_FORMAT, GMCLFFormatClass))
#define G_IS_MCLF_FORMAT_CLASS(klass)     (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_MCLF_FORMAT))
#define G_MCLF_FORMAT_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_MCLF_FORMAT, GMCLFFormatClass))


/* Format d'exécutable MCLF (instance) */
typedef struct _GMCLFFormat GMCLFFormat;

/* Format d'exécutable MCLF (classe) */
typedef struct _GMCLFFormatClass GMCLFFormatClass;


/* Valide un contenu comme étant un format Mobicore. */
bool check_mclf_format(const GBinContent *);

/* Indique le type défini pour un format d'exécutable MCLF. */
GType g_mclf_format_get_type(void);

/* Prend en charge un nouveau format MCLF. */
GExeFormat *g_mclf_format_new(GBinContent *);



#endif  /* _PLUGINS_MOBICORE_MCLF_H */
