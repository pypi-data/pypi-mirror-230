
/* Chrysalide - Outil d'analyse de fichiers binaires
 * compression.h - prototypes pour les facilités de manipulation des archives
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _COMMON_COMPRESSION_H
#define _COMMON_COMPRESSION_H


#include <archive.h>
#include <archive_entry.h>
#include <stdbool.h>


#include "../analysis/content.h"



/* Codes de retour pour la compression */
typedef enum _CPError
{
    CPE_NO_ERROR,                           /* Aucun souci particulier     */
    CPE_SYSTEM_ERROR,                       /* Le soucis vient de l'archive*/
    CPE_ARCHIVE_ERROR                       /* Le soucis vient du système  */

} CPError;


/* Ajoute un élement à une archive. */
CPError add_file_into_archive(struct archive *, const char *, const char *);

/* Extrait un élement d'une archive. */
bool dump_archive_entry_into_file(struct archive *, struct archive_entry *, const char *);

/* Extrait un élement d'une archive. */
GBinContent *dump_archive_entry_into_memory(struct archive *, struct archive_entry *);



#endif  /* _COMMON_COMPRESSION_H */
