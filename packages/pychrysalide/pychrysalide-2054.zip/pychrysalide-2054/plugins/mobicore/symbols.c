
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.c - gestion des symboles d'un MCLF
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


#include "symbols.h"


#include <malloc.h>


#include <mangling/demangler.h>


#include "mclf-int.h"



/* Enregistre un point d'entrée au sein d'un binaire MCLF. */
static void register_mclf_entry_point(GMCLFFormat *, virt_t, phys_t, GBinRoutine *);

/* Enumère les points d'entrée principaux d'un binaire MCLF. */
static bool load_all_mclf_basic_entry_points(GMCLFFormat *format);



/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à compléter.           *
*                vaddr   = adresse virtuelle du symbole à insérer.            *
*                len     = taille de la routine à ajouter.                    *
*                routine = représentation de la fonction repérée.             *
*                                                                             *
*  Description : Enregistre un point d'entrée au sein d'un binaire MCLF.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_mclf_entry_point(GMCLFFormat *format, virt_t vaddr, phys_t len, GBinRoutine *routine)
{
    GBinFormat *base;                   /* Version basique de l'instance   */
    vmpa2t addr;                        /* Localisation d'une routine  */
    mrange_t range;                     /* Couverture mémoire associée */
    GBinSymbol *symbol;                 /* Nouveau symbole construit   */

    base = G_BIN_FORMAT(format);

    /* Comptabilisation pour le désassemblage brut */

    g_binary_format_register_code_point(base, vaddr, DPL_ENTRY_POINT);

    /* Comptabilisation en tant que symbole */

    vaddr &= ~0x1;

	init_vmpa(&addr, vaddr - format->header.v1.text.start, vaddr);
	init_vmpa(&addr, VMPA_NO_PHYSICAL, vaddr);

    init_mrange(&range, &addr, len);

    symbol = G_BIN_SYMBOL(routine);

	g_binary_symbol_set_range(symbol, &range);
    g_binary_symbol_set_stype(symbol, STP_ENTRY_POINT);

	g_binary_format_add_symbol(base, symbol);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                                                                             *
*  Description : Enumère les points d'entrée principaux d'un binaire MCLF.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_all_mclf_basic_entry_points(GMCLFFormat *format)
{
    virt_t ep;                              /* Point d'entrée détecté      */
    GBinRoutine *routine;                   /* Routine à associer à un pt. */

    /* Point d'entrée principal éventuel */

    ep = format->header.v1.entry;

    if (ep != 0x0)
    {
        routine = g_binary_format_decode_routine(G_BIN_FORMAT(format), "entry_point");
        register_mclf_entry_point(format, ep, 0, routine);
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                                                                             *
*  Description : Charge en mémoire la liste humaine des symboles.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_mclf_symbols(GMCLFFormat *format)
{
    bool result;                            /* Bilan à retourner           */

    result = load_all_mclf_basic_entry_points(format);

    return result;

}
