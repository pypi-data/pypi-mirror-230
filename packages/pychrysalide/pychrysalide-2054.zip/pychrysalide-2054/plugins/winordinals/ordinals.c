
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ordinals.c - accès à l'ensemble des ordinaux enregistrés
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "ordinals.h"


#include <ctype.h>
#include <malloc.h>
#include <string.h>


#include "cache_oleaut32.h"
#include "cache_ws2_32.h"
#include "cache_wsock32.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Indique la liste de bibliothèques enregistrées avec ordinaux.*
*                                                                             *
*  Retour      : Liste de fichiers DLL pris en charge.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char **list_register_dlls_for_ordinals(void)
{
    const char **result;                    /* Liste à retourner           */

    result = malloc(3 * sizeof(char *));

    result[0] = strdup("oleaut32.dll");
    result[1] = strdup("ws2_32.dll");
    result[2] = strdup("wsock32.dll");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Indique la liste de bibliothèques enregistrées avec ordinaux.*
*                                                                             *
*  Retour      : Liste de fichiers DLL pris en charge.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *get_symbol_by_ordinal(const char *dll, uint16_t ordinal)
{
    const char *result;                     /* Désignation à retourner     */
    size_t len;                             /* Taille de la chaîne         */
    char *lower_dll;                        /* Version en minuscules       */
    size_t i;                               /* Boucle de parcours          */

    len = strlen(dll);

    lower_dll = malloc(len + 1);

    for (i = 0; i < len; i++)
        lower_dll[i] = tolower(dll[i]);

    lower_dll[len] = '\0';

    if (strcmp(lower_dll, "oleaut32.dll") == 0)
        result = find_oleaut32_name_for_ordinal(ordinal);

    else if (strcmp(lower_dll, "ws2_32.dll") == 0)
        result = find_ws2_32_name_for_ordinal(ordinal);

    else if (strcmp(lower_dll, "wsock32.dll") == 0)
        result = find_wsock32_name_for_ordinal(ordinal);

    else
        result = NULL;

    free(lower_dll);

    return result;

}
