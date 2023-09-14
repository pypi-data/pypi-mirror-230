
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - enregistrement d'une description complète
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


#include "manager.h"


#include <assert.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>



/* Mémorisation de la description d'un identifiant */
struct _instr_desc
{
    char *text;                             /* Contenu humainement lisible */

};



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau gestionnaire de définitions d'identifiant.   *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_desc *create_instruction_description(void)
{
    instr_desc *result;                     /* Définition vierge à renvoyer*/

    result = (instr_desc *)calloc(1, sizeof(instr_desc));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : desc = gestionnaire de définition de description à libérer.  *
*                                                                             *
*  Description : Supprime de la mémoire un gestionnaire de description.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_instruction_description(instr_desc *desc)
{
    if (desc->text != NULL)
        free(desc->text);

    free(desc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : desc = gestionnaire de définition de description à traiter.  *
*                text = valeur du contenu à mémoriser.                        *
*                                                                             *
*  Description : Définit le contenu textuel d'une description.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_instruction_description(instr_desc *desc, const char *text)
{
    const char *start;                      /* Départ réel du contenu      */
    size_t len;                             /* Taille maximale à parcourir */
    char *iter;                             /* Boucle de parcours          */

    for (start = text; *start != '\0'; start++)
        if (!isspace(*start))
            break;

    desc->text = strdup(start);

    len = strlen(desc->text);

    if (len > 0)
    {
        for (iter = desc->text + len - 1;
             iter != desc->text;
             iter--)
        {
            if (isspace(*iter))
                *iter = '\0';
            else
                break;
        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : desc = gestionnaire de définition de description à traiter.  *
*                fd   = flux ouvert en écriture.                              *
*                                                                             *
*  Description : Imprime la description associée à une instruction.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void write_instruction_description(const instr_desc *desc, int fd)
{
    const char *iter;                       /* Boucle de parcours          */

    for (iter = desc->text; *iter != '\0'; iter++)
        switch (*iter)
        {
            case '\n':
                dprintf(fd, "\\n");
                break;

            case '"':
                dprintf(fd, "\\\"");
                break;

            default:
                dprintf(fd, "%c", *iter);
                break;

        }

}
