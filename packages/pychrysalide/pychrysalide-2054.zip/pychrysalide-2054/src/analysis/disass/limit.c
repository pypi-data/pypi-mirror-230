
/* Chrysalide - Outil d'analyse de fichiers binaires
 * limit.c - détermination des bornes des routines
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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


#include "limit.h"


#include <assert.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : symbol   = routine dont les frontières sont à fixer.         *
*                next     = adresse du prochain symbole présent.              *
*                proc     = ensemble d'instructions désassemblées.            *
*                portions = ensemble de couches binaires bornées.             *
*                                                                             *
*  Description : S'assure qu'une routine est bien bornée.                     *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_routine_limit(GBinSymbol *symbol, const vmpa2t *next, GArchProcessor *proc, GBinPortion *portions)
{
    const mrange_t *range;                  /* Emplacement courant         */
    vmpa2t addr;                            /* Adresse à conserver         */
    GArchInstruction *start;                /* Première instruction        */
    GBinPortion *portion;                   /* Conteneur avec limites      */
    phys_t pdiff;                           /* Différence avec ces limites */
    phys_t diff;                            /* Taille définie par déduction*/
    mrange_t new;                           /* Nouvel emplacement taillé   */

    range = g_binary_symbol_get_range(symbol);
    if (get_mrange_length(range) > 0) goto crl_skip;

    copy_vmpa(&addr, get_mrange_addr(range));

    /* Marquage de la première instruction */

    start = g_arch_processor_find_instr_by_address(proc, &addr);

    /**
     * On considère que les symboles chargés à partir du format peuvent
     * être corrompus, potentiellement pour faire planter un analyseur.
     *
     * Donc on s'autorise à être prudent.
     */
    if (start == NULL) goto crl_skip;

    g_arch_instruction_set_flag(start, AIF_ROUTINE_START);

    g_object_unref(G_OBJECT(start));

    /* Dans tous les cas, on va se référer à la portion contenante... */

    portion = g_binary_portion_find_at_addr(portions, &addr);
    assert(portion != NULL);

    range = g_binary_portion_get_range(portion);

    pdiff = compute_vmpa_diff(&addr, get_mrange_addr(range));
    pdiff = get_mrange_length(range) - pdiff;

    g_object_unref(G_OBJECT(portion));

    /* Si on peut se raccrocher à la prochaine adresse... */
    if (next != NULL)
    {
        diff = compute_vmpa_diff(&addr, next);

        /**
         * On considère qu'un symbole ne peut pas déborder d'un segment
         * sur un autre.
         */

        if (diff > pdiff)
            diff = pdiff;

    }

    /* Sinon on va jusqu'à la fin de la zone ! */
    else
        diff = pdiff;

    init_mrange(&new, &addr, diff);

    g_binary_symbol_set_range(symbol, &new);

 crl_skip:

    ;

}
