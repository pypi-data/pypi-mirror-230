
/* Chrysalide - Outil d'analyse de fichiers binaires
 * writer.h - prototypes pour la mise en place de commentaires adaptés aux appels système
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


#ifndef _PLUGINS_LNXSYSCALLS_WRITER_H
#define _PLUGINS_LNXSYSCALLS_WRITER_H


#include <format/preload.h>



/* Mémorisation des commentaires à insérer */
typedef struct _comment_writer comment_writer;


/* Crée un espace de conservation pour commentaires d'appels. */
comment_writer *create_comment_writer(void);

/* Détruit la conservation de commentaires pour appels. */
void delete_comment_writer(comment_writer *);

/* Complète un commentaire ou en insére un nouveau. */
void add_comment_at(comment_writer *, const char *, GArchInstruction *);

/* Applique tous les commentaires à l'écriture anticipée. */
void write_all_comments(comment_writer *, GPreloadInfo *);



#endif  /* _PLUGINS_LNXSYSCALLS_WRITER_H */
