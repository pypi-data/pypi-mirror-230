
/* Chrysalide - Outil d'analyse de fichiers binaires
 * targetable.c - opérandes ciblant une portion de désassemblage
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "targetable.h"


#include "targetable-int.h"



/* Procède à l'initialisation de l'interface de ciblage. */
static void g_targetable_operand_default_init(GTargetableOperandInterface *);



/* Détermine le type d'une interface pour le ciblage d'une portion de désassemblage. */
G_DEFINE_INTERFACE(GTargetableOperand, g_targetable_operand, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de ciblage.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_targetable_operand_default_init(GTargetableOperandInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                src     = localisation de l'instruction mère.                *
*                format  = format reconnu pour le binaire chargé.             *
*                proc    = architecture associée à ce même binaire.           *
*                addr    = localisation de la cible. [OUT]                    *
*                                                                             *
*  Description : Obtient l'adresse de la cible visée par un opérande.         *
*                                                                             *
*  Retour      : true si la cible est valide, false sinon.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_targetable_operand_get_addr(const GTargetableOperand *operand, const vmpa2t *src, GBinFormat *format, GArchProcessor *proc, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GTargetableOperandIface *iface;         /* Interface utilisée          */

    iface = G_TARGETABLE_OPERAND_GET_IFACE(operand);

    result = iface->get_addr(operand, src, format, proc, addr);

    return result;

}
