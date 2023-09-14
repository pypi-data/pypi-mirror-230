
/* Chrysalide - Outil d'analyse de fichiers binaires
 * xdg.c - compléments mineurs au support Freedesktop
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#include "xdg.h"


#include <dirent.h>
#include <errno.h>
#include <glib.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : suffix = élément visé dans le répertoire de configuration.   *
*                                                                             *
*  Description : Détermine le chemin d'un répertoire selon les specs. XDG.    *
*                                                                             *
*  Retour      : Chemin d'accès aux configurations personnelles ou NULL.      *
*                                                                             *
*  Remarques   : cf. http://standards.freedesktop.org/basedir-spec/.          *
*                                                                             *
******************************************************************************/

char *get_xdg_config_dir(const char *suffix)
{
    char *result;                           /* Chemin d'accès à renvoyer   */
    const char *env;                        /* Valeur de l'environnement   */
    DIR *directory;                         /* Répertoire avec contenu ?   */
    struct dirent *entry;                   /* Elément de répertoire       */

    result = NULL;

    env = getenv("XDG_CONFIG_HOME");

    if (env != NULL && env[0] != '\0')
    {
        directory = opendir(env);
        if (directory == NULL) goto default_cfg_dir;

        while (1)
        {
            errno = 0;

            entry = readdir(directory);

            if (entry == NULL)
            {
                if (errno != 0)
                    perror("readdir");

                break;

            }

            if (strcmp(entry->d_name, ".") == 0) continue;
            if (strcmp(entry->d_name, "..") == 0) continue;

            result = (char *)calloc(strlen(env) + 2 + strlen(suffix) + 1, sizeof(char));
            strcpy(result, env);

            if (env[strlen(env) - 1] != G_DIR_SEPARATOR)
                strcat(result, G_DIR_SEPARATOR_S);

            strcat(result, ".");
            strcat(result, suffix);

        }

        closedir(directory);

    }

 default_cfg_dir:

    if (result == NULL)
    {
        env = getenv("HOME");
        if (env == NULL || env[0] == '\0') return NULL;

        result = (char *)calloc(strlen(env) + 1 + strlen(".config" G_DIR_SEPARATOR_S)
                                + strlen(suffix) + 1, sizeof(char));

        strcpy(result, env);

        if (env[strlen(env) - 1] != G_DIR_SEPARATOR)
            strcat(result, G_DIR_SEPARATOR_S);

        strcat(result, ".config" G_DIR_SEPARATOR_S);
        strcat(result, suffix);

    }

    return result;

}
