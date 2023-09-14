
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sqlite.c - extension des définitions propres à SQLite
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "sqlite.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "extstr.h"



/* Attribue une définition aux valeurs paramétrées. */
static bool bind_bound_values(sqlite3 *, sqlite3_stmt *, const char *, const bound_value *, size_t, int *);



/******************************************************************************
*                                                                             *
*  Paramètres  : values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Libère de la mémoire un ensemble de valeurs en fin de vie.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void free_all_bound_values(bound_value *values, size_t count)
{
    size_t i;                               /* Boucle de parcours          */
    bound_value *value;                     /* Valeur à traiter            */

    return;

    for (i = 0; i < count; i++)
    {
        value = values + i;

        if (value->built_name)
            free(value->name);

    }

    if (values != NULL)
        free(values);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                name   = désignation de la valeur recherchée.                *
*                                                                             *
*  Description : Effectue une recherche au sein d'un ensemble de valeurs.     *
*                                                                             *
*  Retour      : Elément retrouvé ou NULL en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const bound_value *find_bound_value(const bound_value *values, size_t count, const char *name)
{
    const bound_value *result;              /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < count && result == NULL; i++)
        if (strcmp(values[i].name, name) == 0)
            result = &values[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db     = base de données à consulter.                        *
*                stmt   = requête SQL en préparation à faire évoluer.         *
*                sql    = définition brute de cette requête SQL.              *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                index  = indice évolutif des valeurs paramétrées. [OUT]      *
*                                                                             *
*  Description : Attribue une définition aux valeurs paramétrées.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool bind_bound_values(sqlite3 *db, sqlite3_stmt *stmt, const char *sql, const bound_value *values, size_t count, int *index)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    int ret;                                /* Bilan d'un appel à SQLite   */

    result = true;

    for (i = 0; i < count && result; i++)
    {
        if (!values[i].has_value)
            continue;

        switch (values[i].type)
        {
            case SQLITE_BOOLEAN:
                ret = sqlite3_bind_int(stmt, *index, values[i].boolean);
                break;

            case SQLITE_INTEGER:
                ret = sqlite3_bind_int(stmt, *index, values[i].integer);
                break;

            case SQLITE_INT64:
                ret = sqlite3_bind_int64(stmt, *index, values[i].integer64);
                break;

            case SQLITE_TEXT:
                ret = sqlite3_bind_text(stmt, *index, values[i].string, -1, values[i].delete);
                break;

            case SQLITE_NULL:
                ret = sqlite3_bind_null(stmt, *index);
                break;

            default:
                assert(false);
                ret = SQLITE_ERROR;
                break;

        }

        if (ret == SQLITE_OK)
            (*index)++;

        else
        {
            result = false;

            fprintf(stderr, "Can't bind value for parameter nb %d in '%s' (ret=%d): %s\n",
                    *index, sql, ret, sqlite3_errmsg(db));

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db     = base de données à consulter.                        *
*                table  = nom de la table concernée.                          *
*                values = champs avec leur valeur.                            *
*                count  = quantité de ces champs.                             *
*                cb     = procédure à appeler pour chaque nouvelle série.     *
*                data   = éventuelles données associées à transmettre.        *
*                                                                             *
*  Description : Charge une série de valeurs depuis une base de données.      *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_db_values(sqlite3 *db, const char *table, bound_value *values, size_t count, db_load_cb cb, void *data)
{
    bool result;                            /* Conclusion à faire remonter */
    char *sql;                              /* Requête SQL à construire    */
    bool first;                             /* Marque du premier passage   */
    size_t i;                               /* Boucle de parcours          */
    sqlite3_stmt *stmt;                     /* Déclaration mise en place   */
    int ret;                                /* Bilan d'un appel à SQLite   */
    int index;                              /* Indice de valeur attachée   */
    int native_type;                        /* Type de valeur dans la base */

    result = false;

    /* Préparation de la requête */

    sql = strdup("SELECT ");

    first = true;

    for (i = 0; i < count; i++)
    {
        if (values[i].has_value)
            continue;

        if (!first) sql = stradd(sql, ", ");

        sql = stradd(sql, values[i].name);

        first = false;

    }

    assert(!first);

    sql = stradd(sql, " FROM ");
    sql = stradd(sql, table);

    first = true;

    for (i = 0; i < count; i++)
    {
        if (!values[i].has_value)
            continue;

        if (first)
            sql = stradd(sql, " WHERE ");
        else
            sql = stradd(sql, " AND ");

        sql = stradd(sql, values[i].name);

        sql = stradd(sql, " = ?");

        first = false;

    }

    sql = stradd(sql, ";");

    ret = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
	if (ret != SQLITE_OK)
    {
		fprintf(stderr, "Can't prepare SELECT statment '%s' (ret=%d): %s\n", sql, ret, sqlite3_errmsg(db));
        goto prepare_error;
	}

    /* Attribution des valeurs */

    index = 1;

    if (!bind_bound_values(db, stmt, sql, values, count, &index))
        goto bind_error;

    /* Chargement des valeurs existantes */

    result = true;

    for (ret = sqlite3_step(stmt); ret == SQLITE_ROW && result; ret = sqlite3_step(stmt))
    {
        /* Conversion des valeurs */

        index = 0;

        for (i = 0; i < count; i++)
        {
            if (values[i].has_value)
                continue;

            native_type = sqlite3_column_type(stmt, index);

            /**
             * On réalise une petite conversion selon le champ.
             *
             * Le filtre SQLITE_NATIVE est destiné à conserver le type choisi par
             * SQLite. Typiquement, une chaîne peut être à SQLITE_NULL ou SQLITE_TEXT
             * selon la valeur conservée dans la base.
             *
             * D'autres éléments, comme les localisations en mémoire, peuvent aussi
             * avoir un champ éventuellement nul, donc la définition à partir des
             * indications de la base de données reste importante.
             *
             * En ce qui concerne les valeurs numériques, SQLite ne fait pas de
             * distinction : tout passe par la fonction sqlite3VdbeIntValue(),
             * qui effectue des transtypages au besoin pour tout ce qui n'est
             * pas numérique.
             *
             * Pour les types internes SQLITE_INTEGER et SQLITE_BOOLEAN,
             * il est donc nécessaire d'ajuster en interne.
             */

            if (native_type == SQLITE_INTEGER)
                native_type = SQLITE_INT64;

            if (values[i].type == SQLITE_NATIVE)
                values[i].type = native_type;

            else
                assert(values[i].type == native_type
                       || values[i].type == SQLITE_INTEGER
                       || values[i].type == SQLITE_BOOLEAN);

            switch (values[i].type)
            {
                case SQLITE_BOOLEAN:
                    values[i].boolean = (bool)sqlite3_column_int(stmt, index);
                    break;

                case SQLITE_INTEGER:
                    values[i].integer = sqlite3_column_int(stmt, index);
                    break;

                case SQLITE_INT64:
                    values[i].integer64 = sqlite3_column_int64(stmt, index);
                    break;

                case SQLITE_FLOAT:
                    assert(0);
                    break;

                case SQLITE_TEXT:
                    values[i].cstring = (const char *)sqlite3_column_text(stmt, index);
                    break;

                case SQLITE_BLOB:
                    assert(0);
                    break;

                case SQLITE_NULL:
                    break;

                default:
                    assert(0);
                    break;

            }

            index++;

        }

        /* Chargement d'un nouvel élément */

        cb(values, count, data);

    }

 bind_error:

    sqlite3_finalize(stmt);

 prepare_error:

    free(sql);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db     = base de données à mettre à jour.                    *
*                table  = nom de la table concernée.                          *
*                values = champs avec leur valeur.                            *
*                count  = quantité de ces champs.                             *
*                                                                             *
*  Description : Enregistre une série de valeurs dans une base de données.    *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool store_db_values(sqlite3 *db, const char *table, const bound_value *values, size_t count)
{
    bool result;                            /* Conclusion à faire remonter */
    char *sql;                              /* Requête SQL à construire    */
    size_t i;                               /* Boucle de parcours          */
    sqlite3_stmt *stmt;                     /* Déclaration mise en place   */
    int ret;                                /* Bilan d'un appel à SQLite   */
    int index;                              /* Indice de valeur attachée   */

    result = false;

    /* Préparation de la requête */

    sql = strdup("INSERT INTO ");
    sql = stradd(sql, table);
    sql = stradd(sql, " (");

    for (i = 0; i < count; i++)
    {
        assert(values[i].has_value);

        if (i > 0) sql = stradd(sql, ", ");

        sql = stradd(sql, values[i].name);

    }

    sql = stradd(sql, ") VALUES (");

    for (i = 0; i < count; i++)
    {
        if (i > 0) sql = stradd(sql, ", ");

        if (values[i].type == SQLITE_RAW)
            sql = stradd(sql, values[i].cstring);
        else
            sql = stradd(sql, "?");

    }

    sql = stradd(sql, ");");

	ret = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
	if (ret != SQLITE_OK)
    {
		fprintf(stderr, "Can't prepare INSERT statment '%s' (ret=%d): %s\n", sql, ret, sqlite3_errmsg(db));
        goto prepare_error;
	}

    /* Attribution des valeurs */

    index = 1;

    if (!bind_bound_values(db, stmt, sql, values, count, &index))
        goto bind_error;

    /* Exécution finale */

	ret = sqlite3_step(stmt);

    if (ret != SQLITE_DONE)
    {
		fprintf(stderr, "INSERT statement '%s' didn't return DONE (ret=%d): %s\n", sql, ret, sqlite3_errmsg(db));
        goto insert_error;
    }

    result = true;

 insert_error:

 bind_error:

    sqlite3_finalize(stmt);

 prepare_error:

    free(sql);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db     = base de données à mettre à jour.                    *
*                table  = nom de la table concernée.                          *
*                values = champs avec leur valeur nouvelle.                   *
*                vcount = quantité de ces champs.                             *
*                values = champs avec leur valeur de condition.               *
*                ccount = quantité de ces champs.                             *
*                                                                             *
*  Description : Met à jour une série de valeurs dans une base de données.    *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool update_db_values(sqlite3 *db, const char *table, const bound_value *values, size_t vcount, const bound_value *conds, size_t ccount)
{
    bool result;                            /* Conclusion à faire remonter */
    char *sql;                              /* Requête SQL à construire    */
    size_t i;                               /* Boucle de parcours          */
    sqlite3_stmt *stmt;                     /* Déclaration mise en place   */
    int ret;                                /* Bilan d'un appel à SQLite   */
    int index;                              /* Indice de valeur attachée   */

    result = false;

    /* Préparation de la requête */

    sql = strdup("UPDATE ");
    sql = stradd(sql, table);
    sql = stradd(sql, " SET");

    for (i = 0; i < vcount; i++)
    {
        assert(values[i].has_value);

        if (i > 0) sql = stradd(sql, " ,");

        sql = stradd(sql, " ");
        sql = stradd(sql, values[i].name);

        sql = stradd(sql, " = ?");

    }

    if (ccount > 0)
    {
        sql = stradd(sql, " WHERE");

        for (i = 0; i < ccount; i++)
        {
            if (i > 0) sql = stradd(sql, " AND");

            sql = stradd(sql, " ");
            sql = stradd(sql, conds[i].name);

            sql = stradd(sql, " = ?");

        }

    }

    sql = stradd(sql, ";");

	ret = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
	if (ret != SQLITE_OK)
    {
		fprintf(stderr, "Can't prepare UPDATE statment '%s' (ret=%d): %s\n", sql, ret, sqlite3_errmsg(db));
        goto prepare_error;
	}

    /* Attribution des valeurs */

    index = 1;

    if (!bind_bound_values(db, stmt, sql, values, vcount, &index))
        goto bind_error;

    if (!bind_bound_values(db, stmt, sql, conds, ccount, &index))
        goto bind_error;

    /* Exécution finale */

	ret = sqlite3_step(stmt);

    if (ret != SQLITE_DONE)
    {
		fprintf(stderr, "UPDATE statement '%s' didn't return DONE (ret=%d): %s\n", sql, ret, sqlite3_errmsg(db));
        goto update_error;
    }

    result = true;

 update_error:

 bind_error:

    sqlite3_finalize(stmt);

 prepare_error:

    free(sql);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : db       = base de données à sauvegarder.                    *
*                filename = fichier de destination pour la sauvegarde.        *
*                                                                             *
*  Description : Effectue une copie d'une base de données en cours d'usage.   *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool backup_db(sqlite3 *db, const char *filename)
{
    bool result;                            /* Conclusion à faire remonter */
    sqlite3 *copy;                          /* Copie de la base de données */
    int ret;                                /* Bilan d'un appel à SQLite   */
    sqlite3_backup *backup;                 /* Gestionnaire de sauvegarde  */

    /**
     * Cf. https://www.sqlite.org/backup.html
     */

    ret = sqlite3_open(filename, &copy);

    if (ret != SQLITE_OK)
    {
        if (copy != NULL)
            sqlite3_close(copy);

        result = false;

        goto exit;

    }

    backup = sqlite3_backup_init(copy, "main", db, "main");

    if (backup == NULL)
        result = false;

    else
    {
        sqlite3_backup_step(backup, -1);
        sqlite3_backup_finish(backup);

        ret = sqlite3_errcode(copy);

        result = (ret == SQLITE_OK);

    }

 exit:

    return result;

}
