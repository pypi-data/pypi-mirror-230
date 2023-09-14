
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.h - prototypes internes pour la conservation sur disque d'objets construits
 *
 * Copyright (C) 2020 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_STORAGE_STORAGE_INT_H
#define _ANALYSIS_STORAGE_STORAGE_INT_H


#include "storage.h"



/* Gestion d'enregistrements spécifiques */
typedef struct _storage_backend_t
{
    char *name;                             /* Désignation du groupe       */

    char *filename;                         /* Nom du fichier associé      */
    int fd;                                 /* Flux d'accès correspondant  */

} storage_backend_t;

/* Définition d'une conservation d'objets construits (instance) */
struct _GObjectStorage
{
    GObject parent;                         /* A laisser en premier        */

    GTypeMemory *tpmem;                     /* Mémorisation de types       */

    char *hash;                             /* Empreinte du contenu        */

    storage_backend_t *backends;            /* Gestionnaires existants     */
    size_t count;                           /* Quantité de gestionnaires   */
    GMutex mutex;                           /* Contrôle d'accès à la liste */

};

/* Définition d'une conservation d'objets construits (classe) */
struct _GObjectStorageClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _ANALYSIS_STORAGE_STORAGE_INT_H */
