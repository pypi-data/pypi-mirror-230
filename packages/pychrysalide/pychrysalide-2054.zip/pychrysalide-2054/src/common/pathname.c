
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pathname.c - manipulation de chemins de fichiers
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#include "pathname.h"


#include <assert.h>
#include <glib.h>
#include <malloc.h>
#include <string.h>
#include <sys/stat.h>


#include "extstr.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : ref    = fichier servant de référence aux calculs.           *
*                target = fichier absolu ciblé par la procédure.              *
*                                                                             *
*  Description : Calcule le chemin relatif entre deux fichiers donnés.        *
*                                                                             *
*  Retour      : Chemin d'accès déterminé.                                    *
*                                                                             *
*  Remarques   : Les chemins de type 'a//b' ne sont pas supportés.            *
*                                                                             *
******************************************************************************/

char *build_relative_filename(const char *ref, const char *target)
{
    char *result;                           /* Chemin à retourner          */
    size_t common;                          /* Taille de la partie commune */
    const char *found;                      /* Séparateur suivant rencontré*/
    size_t ref_next;                        /* Prochain séparateur #1      */
    size_t target_next;                     /* Prochain séparateur #2      */
    int ret;                                /* Bilan d'un appel            */
    unsigned int levels;                    /* Niveaux de décalage         */
    unsigned int i;                         /* Boucle de parcours #1       */

    common = 0;

    /* Recherche d'une base commune */

    while (1)
    {
        found = strchr(ref + common, G_DIR_SEPARATOR);
        if (found == NULL) break;

        ref_next = found - ref;

        found = strchr(target + common, G_DIR_SEPARATOR);
        if (found == NULL) break;

        target_next = found - target;

        /* Comparaison rapide sur la longeur du nom */
        if (ref_next != target_next) break;

        /* Comparaison sur une portion de chemin */
        ret = strncmp(ref + common, target + common, ref_next - common);
        if (ret != 0) break;

        common = ref_next + 1;

    }

    /* Décompte du décalage entre la référence et la cible */

    found = ref + common;

    for (levels = 0; ; levels++)
    {
        found = strchr(found, G_DIR_SEPARATOR);
        if (found == NULL) break;

        found++;

    }

    /* Construction du résultat final */

    result = strdup(target + common);

    for (i = 0; i < levels; i++)
    {
        result = strprep(result, G_DIR_SEPARATOR_S);
        result = strprep(result, "..");
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref    = fichier servant de référence aux calculs.           *
*                target = fichier relatif ciblé par la procédure.             *
*                                                                             *
*  Description : Calcule le chemin absolu d'un fichier par rapport à un autre.*
*                                                                             *
*  Retour      : Chemin d'accès déterminé ou NULL en cas d'erreur.            *
*                                                                             *
*  Remarques   : Les chemins de type 'a//b' ne sont pas supportés.            *
*                                                                             *
******************************************************************************/

char *build_absolute_filename(const char *ref, const char *target)
{
    char *result;                           /* Chemin à retourner          */
    char *last_sep;                         /* Dernier séparateur trouvé   */
    const char *target_base;                /* Base de la relativité       */

    static const char upper[4] = { '.', '.', G_DIR_SEPARATOR, '\0' };

    result = strdup(ref);

    last_sep = strrchr(result, G_DIR_SEPARATOR);
    assert(last_sep != NULL);

    target_base = target;

    /* Remontée des répertoires */
    while (1)
    {
        if (strncmp(target_base, upper, 3) != 0)
            break;

        target_base += 3;

        *last_sep = '\0';
        last_sep = strrchr(result, G_DIR_SEPARATOR);

        /* S'il devient impossible de remonter autant... */
        if (last_sep == NULL) break;

    }

    if (last_sep == NULL)
    {
        free(result);
        result = NULL;
    }
    else
    {
        *(last_sep + 1) = '\0';
        result = stradd(result, target_base);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'accès avec répertoires.                      *
*                                                                             *
*  Description : S'assure que le chemin fourni est bien en place.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mkpath(const char *path)
{
    char tmp[PATH_MAX];                     /* Recopie de travail          */
    size_t len;                             /* Taille du chemin fourni     */
    char *iter;                             /* Boucle de parcours          */
    struct stat info;                       /* Information sur l'existant  */
    int ret;                                /* Bilan d'un appel système    */

    snprintf(tmp, PATH_MAX, "%s", path);
    len = strlen(tmp);

    /* Le chemin fournit ne contient que des répertoires ? */
    if (tmp[len - 1] == G_DIR_SEPARATOR)
        tmp[len - 1] = '\0';

    /* Sinon, on supprime le dernier élément, qui est un fichier */
    else
    {
        iter = strrchr(tmp, G_DIR_SEPARATOR);
        if (iter == NULL) return true;

        *iter = '\0';

    }

    for(iter = tmp + 1; *iter; iter++)
        if(*iter == G_DIR_SEPARATOR)
        {
            *iter = '\0';

            /* Analyse de l'existant */
            if (stat(tmp, &info) == 0)
            {
                if (S_ISDIR(info.st_mode) == 0)
                    return false;
                else
                {
                    *iter = G_DIR_SEPARATOR;
                    continue;
                }
            }

            ret = mkdir(tmp, S_IRWXU);
            if (ret != 0)
            {
                perror("mkdir");
                return false;
            }

            *iter = G_DIR_SEPARATOR;

        }

    /* Analyse de l'existant */
    if (stat(tmp, &info) == 0)
    {
        if (S_ISDIR(info.st_mode) == 0)
            return false;
        else
            return true;
    }

    ret = mkdir(tmp, S_IRWXU);
    if (ret != 0) perror("mkdir");

    return (ret == 0);

}
