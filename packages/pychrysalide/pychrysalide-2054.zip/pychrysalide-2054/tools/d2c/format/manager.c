
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - enregistrement de la définition des opérandes attendus
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#include "manager.h"


#include <malloc.h>


#include "../helpers.h"



/* Mémorisation de la définition d'opérandes */
struct _operands_format
{
    char **types;                           /* Définitions des opérandes   */
    size_t count;                           /* Quantité de définitions     */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau gestionnaire de définitions d'opérandes.     *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

operands_format *create_operands_format(void)
{
    operands_format *result;                /* Définition vierge à renvoyer*/

    result = (operands_format *)calloc(1, sizeof(operands_format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = gestionnaire de définition d'opérandes à libérer.   *
*                                                                             *
*  Description : Supprime de la mémoire un gestionnaire de définitions.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_operands_format(operands_format *format)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < format->count; i++)
        free(format->types[i]);

    if (format->types != NULL)
        free(format->types);

    free(format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = gestionnaire de définition d'opérandes à traiter.   *
*                type   = définitions des opérandes à charger.                *
*                                                                             *
*  Description : Précise le type d'opérandes dont la définition est à charger.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_operands_format_type(operands_format *format, char *type)
{
    format->types = (char **)realloc(format->types, ++format->count * sizeof(char *));

    format->types[format->count - 1] = make_string_upper(type);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec   = spécification servant de base à l'opération.        *
*                fd     = descripteur d'un flux ouvert en écriture.           *
*                arch   = architecture visée par l'opération.                 *
*                prefix = préfixe pour le type de définitions d'opérandes.    *
*                exit   = exprime le besoin d'une voie de sortie. [OUT]       *
*                                                                             *
*  Description : Définit le chargement des opérandes prévus par la définition.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_operands_loading(const operands_format *format, int fd, const char *arch, const char *prefix, bool *exit)
{
    size_t i;                               /* Boucle de parcours          */

    if (format->count == 0)
    {
        fprintf(stderr, "Error: no type defined for operands.\n");
        return false;
    }

    *exit = true;

    dprintf(fd, "\tif (!%s_read_operands(result, format, content, pos, endian, ", arch);

    for (i = 0; i < format->count; i++)
    {
        if (i > 0)
            dprintf(fd, " | ");

        dprintf(fd, "%s%s", prefix, format->types[i]);

    }

    dprintf(fd, "))\n");

    dprintf(fd, "\t\tgoto bad_exit;\n");
    dprintf(fd, "\n");

    return true;

}
