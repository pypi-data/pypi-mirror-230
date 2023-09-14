
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format-int.h - prototypes pour les structures internes du format BOOT.img
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


#ifndef _PLUGINS_BOOTIMG_FORMAT_INT_H
#define _PLUGINS_BOOTIMG_FORMAT_INT_H


#include <format/known-int.h>


#include "format.h"



/* Format d'une image de démarrage (instance) */
struct _GBootImgFormat
{
    GKnownFormat parent;                    /* A laisser en premier        */

    boot_img_hdr header;                    /* Entête du format            */

};

/* Format d'une image de démarrage (classe) */
struct _GBootImgFormatClass
{
    GKnownFormatClass parent;               /* A laisser en premier        */

};


/* Procède à la lecture de l'entête d'une image BOOT.img. */
bool read_bootimg_header(GBootImgFormat *, boot_img_hdr *);



#endif  /* _PLUGINS_BOOTIMG_FORMAT_INT_H */
