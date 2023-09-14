
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helper_arm.c - prise en compte des spécifités ARM pour la recherche de gadgets
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "helper_arm.h"


#include <assert.h>
#include <malloc.h>


#include <common/cpp.h>
#include <plugins/arm/v7/context.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : names = noms attribués aux différents contextes. [OUT]       *
*                                                                             *
*  Description : Etablit une liste des contextes utiles à la recherche.       *
*                                                                             *
*  Retour      : Nombre de contextes gérés pour cette architecture.           *
*                                                                             *
*  Remarques   : Tous les tableaux créés sont à libérer après usage.          *
*                                                                             *
******************************************************************************/

size_t list_rop_contexts_for_arm(char ***names)
{
    size_t result;                          /* Quantité à renvoyer         */

    result = 2;

    (*names) = malloc(result * sizeof(char *));

    (*names)[0] = "Thumb";
    (*names)[1] = "ARM";

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = processeur lié à l'architecture visée.               *
*                index = indice du type de contexte désiré.                   *
*                                                                             *
*  Description : Etablit un contexte utile et adapté à une recherche.         *
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GProcContext *get_rop_contexts_for_arm(const GArchProcessor *proc, size_t index)
{
    GProcContext *result;                   /* Contexte à retourner        */

    result = g_arch_processor_get_context(proc);

    switch (index)
    {
        /* Thumb */
        case 0:
            g_armv7_context_define_encoding(G_ARMV7_CONTEXT(result), 0, AV7IS_THUMB);
            break;

        /* ARM */
        case 1:
            g_armv7_context_define_encoding(G_ARMV7_CONTEXT(result), 0, AV7IS_ARM);
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : count = nombre d'éléments du tableau retourné. [OUT]         *
*                                                                             *
*  Description : Définit les tailles possibles d'une instruction recherchée.  *
*                                                                             *
*  Retour      : Liste de tailles plausibles.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const phys_t *setup_instruction_sizes_for_arm(size_t *count)
{
    const phys_t *result;                   /* Liste de taille à renvoyer  */

    static const phys_t arm_sizes[] = { 2, 4 };

    result = arm_sizes;

    *count = ARRAY_SIZE(arm_sizes);;

    return result;

}
