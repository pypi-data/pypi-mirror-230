
/* Chrysalide - Outil d'analyse de fichiers binaires
 * mclf-int.h - prototypes pour les structures internes du format MCLF
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


#ifndef _PLUGINS_MOBICORE_MCLF_INT_H
#define _PLUGINS_MOBICORE_MCLF_INT_H


#include <common/endianness.h>
#include <format/executable-int.h>


#include "mclf.h"
#include "mclf-def.h"



/* Format d'exécutable MCLF (instance) */
struct _GMCLFFormat
{
    GExeFormat parent;                      /* A laisser en premier        */

    mclf_header_t header;                   /* En-tête du format           */
    SourceEndian endian;                    /* Boutisme du format          */

};

/* Format d'exécutable MCLF (classe) */
struct _GMCLFFormatClass
{
    GExeFormatClass parent;                 /* A laisser en premier        */

};



/* Procède à la lecture de l'en-tête d'un contenu binaire MCLF. */
bool read_mclf_header(GMCLFFormat *, mclf_header_t *, SourceEndian);

/* Procède à la lecture d'un descripteur de segment MCLF. */
bool read_mclf_segment_desc(GMCLFFormat *, segment_descriptor_t *, vmpa2t *, SourceEndian);



#endif  /* _PLUGINS_MOBICORE_MCLF_INT_H */
