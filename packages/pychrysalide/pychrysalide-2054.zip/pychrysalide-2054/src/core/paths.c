
/* Chrysalide - Outil d'analyse de fichiers binaires
 * paths.c - récupération de fichiers secondaires
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


#include "paths.h"


#include <assert.h>
#include <dlfcn.h>
#include <glib.h>
#include <libgen.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


#include <config.h>


#include "logs.h"
#include "../common/extstr.h"



/* Eventuelle nouvelle racine de substitution */
static const char *_new_prefix = NULL;


/* Trouve le chemin d'accès complet à un fichier donné. */
static char *find_file_in_directory(const char *, const char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : new = nouvelle racine pour les répertoires.                  *
*                                                                             *
*  Description : Enregistre un répertoire comme nouvelle base de construction.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_new_prefix(const char *new)
{
    _new_prefix = new;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : template = répertoire de travail visé.                       *
*                                                                             *
*  Description : Fournit le répertoire réel correspondant à une cible.        *
*                                                                             *
*  Retour      : Répertoire de travail effectif.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_effective_directory(const char *template)
{
    char *result;                           /* Répertoire à retourner      */
    size_t len;                             /* Taille de comparaison       */

    result = NULL;

    if (_new_prefix == NULL)
        goto use_default;

    len = strlen(BUILD_PREFIX_DIR);

    if (strncmp(template, BUILD_PREFIX_DIR, len) == 0)
    {
        result = strdup(_new_prefix);
        result = stradd(result, template + len);
    }

 use_default:

    if (result == NULL)
        result = strdup(template);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de répertoire de travail visé.                   *
*                                                                             *
*  Description : Fournit le répertoire réel correspondant à une cible.        *
*                                                                             *
*  Retour      : Répertoire de travail effectif.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_effective_directory_new(TargetDirectoryType type)
{
    char *result;                           /* Répertoire à retourner      */
#ifdef DISCARD_LOCAL
    Dl_info info;                           /* Informations dynamiques     */
    int ret;                                /* Bilan d'une récupération    */
    char *dyn_path_tmp;                     /* Chemin d'accès modifiable   */
    const char *dyn_path;                   /* Chemin d'accès courant      */
#   ifdef PYTHON_PACKAGE
    size_t len;                             /* Taille de comparaison       */
    size_t pos;                             /* Position dans une chaîne    */
#   endif
#endif

    /**
     * Toutes les définitions traitées dans cette fonction doivent rester synchronisées
     * avec celles du fichier configure.ac.
     *
     * Quand les ressources issues du code source ne sont pas utilisées, deux cas de
     * figure sont pris en compte :
     *
     *   - .../lib
     *   - .../lib/chrysalide-plugins
     *
     *   - .../lib/python3.7/site-packages/chrysalide-libs
     *   - .../lib/python3.7/site-packages
     *
     * Le chemin courant pointe sur le premier élément et doit permettre de retrouver
     * les autres sur demandes.
     */

    result = NULL;

#ifdef DISCARD_LOCAL

    ret = dladdr(__FUNCTION__, &info);
    if (ret == 0)
    {
        LOG_ERROR_DL_N("dladdr");
        goto exit;
    }

    dyn_path_tmp = strdup(info.dli_fname);
    dyn_path = dirname(dyn_path_tmp);

#endif

    switch (type)
    {
        case TDT_PLUGINS_LIB:

#ifndef DISCARD_LOCAL
            result = strdup(PACKAGE_SOURCE_DIR G_DIR_SEPARATOR_S "plugins");
#else
#   ifdef PYTHON_PACKAGE

            len = strlen("chrysalide-libs");
            pos = strlen(dyn_path);

            if (pos <= len)
                goto bad_sync;

            pos -= len;

            if (strcmp(&dyn_path[pos], "chrysalide-libs") != 0)
                goto bad_sync;

            result = strdup(dyn_path);
            result[pos] = '\0';
            result = stradd(result, "chrysalide-plugins");

#   else
            result = strdup(dyn_path);
            result = stradd(result, G_DIR_SEPARATOR_S "chrysalide-plugins");
#   endif
#endif
            break;

        default:
            result = NULL;
            break;

    }

#ifdef DISCARD_LOCAL

#   ifdef PYTHON_PACKAGE

 bad_sync:

#   endif

    free(dyn_path_tmp);

 exit:

#endif

    assert(result != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dirname  = répertoire de travail à fouiller.                 *
*                filename = nom de fichier seul comme indice.                 *
*                                                                             *
*  Description : Trouve le chemin d'accès complet à un fichier donné.         *
*                                                                             *
*  Retour      : Chemin trouvé à libérer de la mémoire ou NULL.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *find_file_in_directory(const char *dirname, const char *filename)
{
    char *result;                           /* Trouvaille à renvoyer       */
    int ret;                                /* Bilan du test de présence   */

    asprintf(&result, "%s%s%s", dirname, G_DIR_SEPARATOR_S, filename);

    ret = access(result, F_OK);

    if (ret != 0)
    {
        free(result);
        result = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = nom de fichier seul comme indice.                 *
*                                                                             *
*  Description : Trouve le chemin d'accès complet à un fichier d'image.       *
*                                                                             *
*  Retour      : Chemin trouvé à libérer de la mémoire ou NULL.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *find_pixmap_file(const char *filename)
{
    char *result;                           /* Trouvaille à renvoyer       */
    char *edir;                             /* Répertoire de base effectif */

    /**
     * On privilégie si possible les sources fraiches.
     */

#ifndef DISCARD_LOCAL

    result = find_file_in_directory(PACKAGE_SOURCE_DIR G_DIR_SEPARATOR_S "pixmaps", filename);

#else

    result = NULL;

#endif

    if (result == NULL)
    {
        edir = get_effective_directory(PIXMAPS_DIR);
        result = find_file_in_directory(edir, filename);
        free(edir);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pgname   = nom du greffon concerné.                          *
*                filename = nom de fichier seul comme indice.                 *
*                                                                             *
*  Description : Trouve le chemin d'accès complet à un fichier de greffon.    *
*                                                                             *
*  Retour      : Chemin trouvé à libérer de la mémoire ou NULL.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *find_plugin_data_file(const char *pgname, const char *filename)
{
    char *result;                           /* Trouvaille à renvoyer       */
#ifndef DISCARD_LOCAL
    char *dirname;                          /* Répertoire à cibler         */
#endif
    char *edir;                             /* Répertoire de base effectif */

    /**
     * On privilégie si possible les sources fraiches.
     */

#ifndef DISCARD_LOCAL

    asprintf(&dirname, "%s%splugins%s%s",
             PACKAGE_SOURCE_DIR, G_DIR_SEPARATOR_S, G_DIR_SEPARATOR_S, pgname);

    result = find_file_in_directory(dirname, filename);

    free(dirname);

#else

    result = NULL;

#endif

    if (result == NULL)
    {
        edir = get_effective_directory(PLUGINS_DATA_DIR);
        result = find_file_in_directory(edir, filename);
        free(edir);
    }

    return result;

}
