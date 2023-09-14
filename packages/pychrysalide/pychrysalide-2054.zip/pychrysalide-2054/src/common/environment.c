
/* Chrysalide - Outil d'analyse de fichiers binaires
 * environment.c - manipulations des variables d'environnement.
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "environment.h"


#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "extstr.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation de la variable à traiter.                 *
*                                                                             *
*  Description : Fournit le contenu d'une variable d'environnement.           *
*                                                                             *
*  Retour      : Chaîne à libérer de la mémoire après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_env_var(const char *name)
{
    char *result;                           /* Chaîne à retourner          */

    result = getenv(name);

    if (result == NULL) result = strdup("");
    else result = strdup(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name  = désignation de la variable à traiter.                *
*                value = valeur à ajouter à la variable.                      *
*                sep   = séparateur entre champs.                             *
*                                                                             *
*  Description : Complète le contenu d'une variable d'environnement.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_to_env_var(const char *name, const char *value, const char *sep)
{
    char *content;                          /* Contenu final à définir     */
    int ret;                                /* Bilan d'un appel système    */

    content = get_env_var(name);

    if (strlen(content) > 0) content = stradd(content, sep);

    content = stradd(content, value);

    ret = setenv(name, content, 1);
    if (ret != 0) perror("setenv");

    free(content);

    return (ret == 0);

}
