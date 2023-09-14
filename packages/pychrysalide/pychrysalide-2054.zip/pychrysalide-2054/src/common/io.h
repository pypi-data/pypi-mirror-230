
/* Chrysalide - Outil d'analyse de fichiers binaires
 * io.h - prototypes pour des entrées sorties fiables
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


#ifndef _COMMON_IO_H
#define _COMMON_IO_H


#include <stdbool.h>
#include <sys/types.h>



/* Lit des données depuis un flux local. */
bool safe_read(int, void *, size_t);

/* Lit des données depuis un flux local. */
ssize_t safe_read_partial(int, void *, size_t);

/* Ecrit des données dans un flux local. */
bool safe_write(int, const void *, size_t);

/* Réceptionne des données depuis un flux réseau. */
bool safe_recv(int, void *, size_t, int);

/* Envoie des données au travers un flux réseau. */
bool safe_send(int, const void *, size_t, int);

/* S'assure qu'un chemin donné existe dans le système. */
int ensure_path_exists(const char *);

/* Met en place un fichier temporaire. */
int make_tmp_file(const char *, const char *, char **);

/* Copie un fichier. */
bool copy_file(const char *, const char *);



#endif  /* _COMMON_IO_H */
