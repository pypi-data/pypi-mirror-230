
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sqlite.h - prototypes pour une extension des définitions propres à SQLite
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


#ifndef _COMMON_SQLITE_H
#define _COMMON_SQLITE_H


#include <sqlite3.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/types.h>



/* Type pour les insertions brutes */
#define SQLITE_RAW      0                   /* En dur dans une requête     */
#define SQLITE_INT64    10                  /* Entier sur 64 bits          */
#define SQLITE_BOOLEAN  11                  /* Booléen sur 1 bit           */
#define SQLITE_NATIVE   12                  /* Déterminé par la base       */


/* Description des champs et de leur valeur associée */
typedef struct _bound_value
{
    union
    {
        char *name;                         /* Nom du champ à manipuler #1 */
        const char *cname;                  /* Nom du champ à manipuler #2 */

    };
    bool built_name;                        /* Nom à libérer après usage   */

    unsigned int type;                      /* Type de valeur à associer   */

    bool has_value;                         /* Validité des champs suivants*/

    union
    {
        bool boolean;                       /* Etat sur 1 bit              */
        int32_t integer;                    /* Nombre sur 32 bits          */
        int64_t integer64;                  /* Nombre sur 64 bits          */
        char *string;                       /* Chaîne de caractères #1     */
        const char *cstring;                /* Chaîne de caractères #2     */

    };

    void (* delete) (void *);               /* Suppression éventuelle      */

} bound_value;


/* Libère de la mémoire un ensemble de valeurs en fin de vie. */
void free_all_bound_values(bound_value *, size_t);

/* Effectue une recherche au sein d'un ensemble de valeurs. */
const bound_value *find_bound_value(const bound_value *, size_t, const char *);

/* Interagit avec des valeurs chargées. */
typedef bool (* db_load_cb) (const bound_value *, size_t, void *);

/* Charge une série de valeurs depuis une base de données. */
bool load_db_values(sqlite3 *, const char *, bound_value *, size_t, db_load_cb, void *);

/* Enregistre une série de valeurs dans une base de données. */
bool store_db_values(sqlite3 *, const char *, const bound_value *, size_t);

/* Met à jour une série de valeurs dans une base de données. */
bool update_db_values(sqlite3 *, const char *, const bound_value *, size_t, const bound_value *, size_t);

/* Effectue une copie d'une base de données en cours d'usage. */
bool backup_db(sqlite3 *, const char *);



#endif  /* _COMMON_SQLITE_H */
