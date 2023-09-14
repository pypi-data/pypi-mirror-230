
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - enregistrement de la définition d'un identifiant
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
#include <malloc.h>
#include <stdbool.h>



/* Mémorisation de la définition d'un identifiant */
struct _instr_id
{
    unsigned int value;                     /* Identifiant numérique unique*/
    bool set;                               /* Validité de la valeur       */

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

instr_id *create_instruction_id(void)
{
    instr_id *result;                       /* Définition vierge à renvoyer*/

    result = (instr_id *)calloc(1, sizeof(instr_id));

    result->set = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id = gestionnaire de définition d'identifiant à libérer.     *
*                                                                             *
*  Description : Supprime de la mémoire un gestionnaire d'identifiant.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_instruction_id(instr_id *id)
{
    free(id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id    = gestionnaire de définition d'identifiant à traiter.  *
*                value = valeur à attribuer à une instruction.                *
*                                                                             *
*  Description : Associe une valeur unique à une instruction.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_instruction_id_value(instr_id *id, unsigned int value)
{
    id->value = value;
    id->set = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id = gestionnaire de définition d'identifiant à traiter.     *
*                                                                             *
*  Description : Associe une valeur unique à une instruction.                 *
*                                                                             *
*  Retour      : Valeur attribuée à une instruction.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int get_instruction_id_value(const instr_id *id)
{
    assert(id->set);

    return id->value;

}
