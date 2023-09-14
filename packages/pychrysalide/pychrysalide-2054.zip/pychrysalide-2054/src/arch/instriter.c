
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instriter.h - prototypes pour le parcours simplifié d'un ensemble d'instructions
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "instriter.h"


#include <malloc.h>


#include "processor.h"



/* Suivi d'un parcours d'instructions */
typedef struct _instr_iter_t
{
    GArchProcessor *proc;                   /* Conteneur associé           */
    unsigned int stamp;                     /* Suivi d'évolutions externes */

    size_t index;                           /* Instruction courante        */

    mrange_t restriction;                   /* Enventuelle limite de zone  */
    bool is_restricted;                     /* Validité de l'étendue       */

} instr_iter_t;



/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = processeur recensant diverses instructions.          *
*                index = indice de la première instruction à fournir.         *
*                                                                             *
*  Description : Construit un itérateur pour parcourir des instructions.      *
*                                                                             *
*  Retour      : Itérateur prêt à emploi.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_iter_t *create_instruction_iterator(GArchProcessor *proc, size_t index)
{
    instr_iter_t *result;                   /* Structure à retourner       */

    result = (instr_iter_t *)malloc(sizeof(instr_iter_t));

    g_object_ref(G_OBJECT(proc));

    result->proc = proc;
    result->stamp = g_arch_processor_get_stamp(proc);

    result->index = index;

    result->is_restricted = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à copie.                                    *
*                                                                             *
*  Description : Duplique un itérateur de parcours d'instructions existant.   *
*                                                                             *
*  Retour      : Itérateur prêt à emploi.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_iter_t *copy_instruction_iterator(const instr_iter_t *iter)
{
    instr_iter_t *result;                   /* Structure à retourner       */

    result = (instr_iter_t *)malloc(sizeof(instr_iter_t));

    g_object_ref(G_OBJECT(iter->proc));

    result->proc = iter->proc;
    result->stamp = iter->stamp;

    result->index = iter->index;

    result->is_restricted = iter->is_restricted;

    if (result->is_restricted)
        copy_mrange(&result->restriction, &iter->restriction);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à traiter.                                  *
*                                                                             *
*  Description : Détruit un itérateur mis en place.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_instruction_iterator(instr_iter_t *iter)
{
    g_object_unref(G_OBJECT(iter->proc));

    free(iter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter  = itérateur à traiter.                                 *
*                range = bornes de l'espace de parcours.                      *
*                                                                             *
*  Description : Limite le parcours des instructions à une zone donnée.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void restrict_instruction_iterator(instr_iter_t *iter, const mrange_t *range)
{
    instr_iter_t *new;                      /* Itérateur actualisé         */

    new = g_arch_processor_get_iter_from_address(iter->proc, get_mrange_addr(range));

    if (new)
    {
        iter->index = new->index;
        delete_instruction_iterator(new);
    }

    copy_mrange(&iter->restriction, range);

    iter->is_restricted = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit l'instruction courante de l'itérateur.               *
*                                                                             *
*  Retour      : Instruction suivante trouvée, ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *get_instruction_iterator_current(instr_iter_t *iter)
{
    GArchInstruction *result;               /* Résultat à retourner        */
    const mrange_t *irange;                 /* Emplacement d'instruction   */

    g_arch_processor_lock(iter->proc);

    if (iter->stamp != g_arch_processor_get_stamp(iter->proc))
        result = NULL;

    else
    {
        if (iter->index < g_arch_processor_count_instructions(iter->proc))
        {
            result = g_arch_processor_get_instruction(iter->proc, iter->index);

            /* L'instruction sort-elle des clous ? */
            if (iter->is_restricted)
            {
                irange = g_arch_instruction_get_range(result);

                if (!mrange_contains_mrange(&iter->restriction, irange))
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

        }

        else
            result = NULL;

    }

    g_arch_processor_unlock(iter->proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit l'instruction qui en précède une autre.              *
*                                                                             *
*  Retour      : Instruction suivante trouvée, ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *get_instruction_iterator_prev(instr_iter_t *iter)
{
    GArchInstruction *result;               /* Résultat à retourner        */
    const mrange_t *irange;                 /* Emplacement d'instruction   */

    g_arch_processor_lock(iter->proc);

    if (iter->stamp != g_arch_processor_get_stamp(iter->proc))
        result = NULL;

    else
    {
        if (iter->index > 1)
        {
            iter->index--;
            result = g_arch_processor_get_instruction(iter->proc, iter->index);

            /* L'instruction sort-elle des clous ? */
            if (iter->is_restricted)
            {
                irange = g_arch_instruction_get_range(result);

                if (!mrange_contains_mrange(&iter->restriction, irange))
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

        }

        else
            result = NULL;

    }

    g_arch_processor_unlock(iter->proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit l'instruction qui en suit une autre.                 *
*                                                                             *
*  Retour      : Instruction suivante trouvée, ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *get_instruction_iterator_next(instr_iter_t *iter)
{
    GArchInstruction *result;               /* Résultat à retourner        */
    const mrange_t *irange;                 /* Emplacement d'instruction   */

    g_arch_processor_lock(iter->proc);

    if (iter->stamp != g_arch_processor_get_stamp(iter->proc))
        result = NULL;

    else
    {
        if ((iter->index + 1) < g_arch_processor_count_instructions(iter->proc))
        {
            iter->index++;
            result = g_arch_processor_get_instruction(iter->proc, iter->index);

            /* L'instruction sort-elle des clous ? */
            if (iter->is_restricted)
            {
                irange = g_arch_instruction_get_range(result);

                if (!mrange_contains_mrange(&iter->restriction, irange))
                {
                    g_object_unref(G_OBJECT(result));
                    result = NULL;
                }

            }

        }

        else
            result = NULL;

    }

    g_arch_processor_unlock(iter->proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = itérateur à consulter.                                *
*                                                                             *
*  Description : Détermine s'il reste une instruction dans l'itération.       *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_instruction_iterator_next(const instr_iter_t *iter)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstruction *instr;                /* Prochaine instruction       */
    const mrange_t *irange;                 /* Emplacement d'instruction   */

    g_arch_processor_lock(iter->proc);

    if (iter->stamp != g_arch_processor_get_stamp(iter->proc))
        result = false;

    else
    {
        if ((iter->index + 1) < g_arch_processor_count_instructions(iter->proc))
        {
            instr = g_arch_processor_get_instruction(iter->proc, iter->index + 1);

            /* L'instruction sort-elle des clous ? */
            if (iter->is_restricted)
            {
                irange = g_arch_instruction_get_range(instr);

                result = mrange_contains_mrange(&iter->restriction, irange);

            }

            else
                result = true;

            g_object_unref(G_OBJECT(instr));

        }
        else
            result = false;
    }

    g_arch_processor_unlock(iter->proc);

    return result;


}
