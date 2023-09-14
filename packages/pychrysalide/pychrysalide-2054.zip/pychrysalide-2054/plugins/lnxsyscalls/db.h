
/* Chrysalide - Outil d'analyse de fichiers binaires
 * db.h - prototypes pour la constitution d'identités d'appels depuis une base de données
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


#ifndef _PLUGINS_LNXSYSCALLS_DB_H
#define _PLUGINS_LNXSYSCALLS_DB_H


#include <sqlite3.h>


#include <plugins/plugin.h>


#include "syscall.h"



/* Ouvre la base de connaissances quant aux appels système. */
sqlite3 *open_syscalls_database(void);

/* Ferme la base de connaissances quant aux appels système. */
void close_syscalls_database(sqlite3 *);

/* Présente le contenu de la base des appels système. */
void introduce_syscalls_database(sqlite3 *);

/* Construit l'identité d'un appel système pour un indice donné. */
syscall_info_t *extract_from_syscalls_database(sqlite3 *, const char *, unsigned int);



#endif  /* _PLUGINS_LNXSYSCALLS_DB_H */
