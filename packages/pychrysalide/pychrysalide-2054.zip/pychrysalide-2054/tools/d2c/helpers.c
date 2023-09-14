
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.c - fonctionnalités d'assitance à la compilation
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


#include "helpers.h"


#include <malloc.h>
#include <string.h>



/* ---------------------------------------------------------------------------------- */
/*                              MANIPULATIONS DE CHAINES                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : str = chaîne de caractères à manipuler. [OUT]                *
*                                                                             *
*  Description : Bascule toute une chaîne de caractères en (min|maj)uscules.  *
*                                                                             *
*  Retour      : Pointeur sur la chaîne fournie.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *_make_string_xxx(char *str, int (* fn) (int))
{
    size_t max;                             /* Empleur du parcours         */
    size_t i;                               /* Boucle de parcours          */

    max = strlen(str);

    for (i = 0; i < max; i++)
        str[i] = fn(str[i]);

    return str;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw     = données brutes en provenance de l'analyseur.       *
*                details = indique la nature de la chaîne à traiter.          *
*                                                                             *
*  Description : Traduit une chaîne en élément de fonction C.                 *
*                                                                             *
*  Retour      : Chaîne à libérer de la mémoire après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *make_callable(const char *raw, bool details)
{
    char *result;                           /* Nom formaté à retourner     */
    size_t max;                             /* Empleur du parcours         */
    size_t i;                               /* Boucle de parcours          */

    result = strdup(raw);

    max = strlen(result);

    /* Première passe : on vire les virgules */

    for (i = 0; i < max; i++)
        if (result[i] == ',')
        {
            memmove(result + i, result + i + 1, max - i - 1);
            max--;
        }

    result[max] = '\0';

    /* Deuxième passe : on bascule en minuscules */

    result = make_string_lower(result);

    /* Troisième passe : on remplace les mauvais caractères */

    for (i = 0; i < max; i++)
        switch (result[i])
        {
            case 'a' ... 'z':
            case '0' ... '9':
                break;
            case '-':
                result[i] = '_';
                break;
            default:
                result[i] = (i + 1 == max ? '\0' : '_');
                break;
        }

    /**
     * Dernière passe : on s'assure que le premier caractère n'est pas une lettre.
     * On ajoute ici le préfixe '_' utilisé lors de la génération de prototypes ;
     * en cas d'absence de détails, on ne se retrouve ainsi pas avec un '_' isolé.
     */

    if (details && result[0] != '_')
    {
        max = strlen(result) + 1;
        result = (char *)realloc(result, max);
        memmove(result + 1, result, max);
        result[0] = '_';
    }

    /* Ultime passe : supression des '_' groupés */

    for (i = 0; i < max; i++)
        if (result[i] == '_' && result[i + 1] == '_')
        {
            memmove(result + i + 1, result + i + 2, max - i - 1);
            max--;
            i--;
        }

    return result;

}
