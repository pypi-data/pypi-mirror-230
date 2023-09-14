
/* Chrysalide - Outil d'analyse de fichiers binaires
 * db.c - constitution d'identités d'appels depuis une base de données
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


#include "db.h"


#include <assert.h>
#include <malloc.h>


#include <i18n.h>


#include <core/paths.h>
#include <plugins/self.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Ouvre la base de connaissances quant aux appels système.     *
*                                                                             *
*  Retour      : Base de données SQLite disponible ou NULL en cas d'échec.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

sqlite3 *open_syscalls_database(void)
{
    sqlite3 *result;                    /* Base de données à renvoyer  */
    char *filename;                     /* Chemin vers la base         */
    int ret;                            /* Bilan d'un appel            */

    filename = find_plugin_data_file("lnxsyscalls", "linux-syscalls.db");

    if (filename == NULL)
    {
        log_plugin_simple_message(LMT_ERROR, _("Unable to find the syscalls database"));
        result = NULL;
    }

    else
    {
        ret = sqlite3_open(filename, &result);

        if (ret != SQLITE_OK)
        {
            log_plugin_simple_message(LMT_ERROR, _("Unable to load the syscalls database"));
            result = NULL;
        }

        free(filename);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db = base de données SQLite à clôturer.                      *
*                                                                             *
*  Description : Ferme la base de connaissances quant aux appels système.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void close_syscalls_database(sqlite3 *db)
{
#ifndef NDEBUG
    int ret;                            /* Bilan d'un appel            */
#endif

#ifndef NDEBUG

    ret = sqlite3_close(db);
    assert(ret == SQLITE_OK);

#else

    sqlite3_close(db);

#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db = base de données SQLite à consulter.                     *
*                                                                             *
*  Description : Présente le contenu de la base des appels système.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void introduce_syscalls_database(sqlite3 *db)
{
    const char *sql;                        /* Requête SQL à construire    */
    sqlite3_stmt *stmt;                     /* Déclaration mise en place   */
    int ret;                                /* Bilan d'un appel à SQLite   */

    sql = "SELECT arch, COUNT(nr) FROM Syscalls GROUP BY arch ORDER BY arch;";

	ret = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
	if (ret != SQLITE_OK)
    {
        log_plugin_variadic_message(LMT_ERROR, _("Can't prepare statment '%s' (ret=%d): %s"),
                                    sql, ret, sqlite3_errmsg(db));
        goto isd_exit;
	}

    for (ret = sqlite3_step(stmt); ret == SQLITE_ROW; ret = sqlite3_step(stmt))
    {
        log_plugin_variadic_message(LMT_INFO, _("The database contains %d syscalls for the '%s' architecture"),
                                    sqlite3_column_int(stmt, 1),
                                    (char *)sqlite3_column_text(stmt, 0));
    }

    sqlite3_finalize(stmt);

 isd_exit:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db   = base de données SQLite à consulter.                   *
*                arch = architecture visée par la procédure.                  *
*                nr   = indice de l'appel système à décrire.                  *
*                                                                             *
*  Description : Construit l'identité d'un appel système pour un indice donné.*
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

syscall_info_t *extract_from_syscalls_database(sqlite3 *db, const char *arch, unsigned int nr)
{
    syscall_info_t *result;                 /* Description à retourner     */
    const char *sql;                        /* Requête SQL à construire    */
    size_t i;                               /* Boucle de parcours          */
    sqlite3_stmt *stmt;                     /* Déclaration mise en place   */
    int ret;                                /* Bilan d'un appel à SQLite   */
    const char *arg;                        /* Eventuel argument d'appel   */

    result = NULL;

    sql = "SELECT name, arg_0, arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, filename, line" \
        " FROM Syscalls" \
        " WHERE arch = ? AND nr = ?;";

	ret = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
	if (ret != SQLITE_OK)
    {
        log_plugin_variadic_message(LMT_ERROR, _("Can't prepare statment '%s' (ret=%d): %s"),
                                    sql, ret, sqlite3_errmsg(db));
        goto efsd_exit;
	}

    ret = sqlite3_bind_text(stmt, 1, arch, -1, NULL);
    if (ret != SQLITE_OK)
    {
        log_plugin_variadic_message(LMT_ERROR, _("Can't bind value for parameter nb 0 in '%s' (ret=%d): %s"),
                                    sql, ret, sqlite3_errmsg(db));
        goto efsd_clean_exit;
    }

    ret = sqlite3_bind_int(stmt, 2, nr);
    if (ret != SQLITE_OK)
    {
        log_plugin_variadic_message(LMT_ERROR, _("Can't bind value for parameter nb 1 in '%s' (ret=%d): %s"),
                                    sql, ret, sqlite3_errmsg(db));
        goto efsd_clean_exit;
    }

    ret = sqlite3_step(stmt);

    if (ret == SQLITE_ROW)
    {
        result = create_syscall_info(nr, (char *)sqlite3_column_text(stmt, 0));

        for (i = 0; i < 6; i++)
        {
            arg = (char *)sqlite3_column_text(stmt, 1 + i);

            if (arg != NULL)
                append_arg_to_syscall_info(result, arg);

        }

    }

 efsd_clean_exit:

    sqlite3_finalize(stmt);

 efsd_exit:

    return result;

}
