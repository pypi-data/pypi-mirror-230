
/* Chrysalide - Outil d'analyse de fichiers binaires
 * syscall.h - prototypes pour la définition d'appels système Linux
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


#include "syscall.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : nr   = indice de l'appel système à décrire.                  *
*                name = désignation humaine de ce même appel système.         *
*                                                                             *
*  Description : Crée un début de description d'appel système.                *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

syscall_info_t *create_syscall_info(unsigned int nr, const char *name)
{
    syscall_info_t *result;                 /* Description à retourner     */

    result = (syscall_info_t *)calloc(1, sizeof(syscall_info_t));

    result->nr = nr;
    result->name = strdup(name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = description d'appel système à supprimer.              *
*                                                                             *
*  Description : Efface de la mémoire une description d'appel système.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_syscall_info(syscall_info_t *info)
{
    size_t i;                               /* Boucle de parcours          */

    free(info->name);

    for (i = 0; i < info->argc; i++)
        free(info->argv[i]);

    if (info->filename != NULL)
        free(info->filename);

    free(info);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = description d'appel système à compléter.              *
*                arg  = description d'un argument supplémentaire.             *
*                                                                             *
*  Description : Ajoute un argument à une description d'appel système.        *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void append_arg_to_syscall_info(syscall_info_t *info, const char *arg)
{
    assert(info->argc < 6);

    info->argv[info->argc++] = strdup(arg);

}
