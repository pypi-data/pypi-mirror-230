
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rename.c - opérandes pouvant être renommées
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


#include "rename.h"


#include "rename-int.h"



/* ------------------------ INTERFACE POUR OPERANDE RENOMMEE ------------------------ */


/* Procède à l'initialisation de l'interface de renommage. */
static void g_renamed_operand_default_init(GRenamedOperandInterface *);



/* ----------------------- INTERFACE POUR OPERANDE RENOMMABLE ----------------------- */


/* Procède à l'initialisation de l'interface de renommage. */
static void g_renameable_operand_default_init(GRenameableOperandInterface *);



/* ---------------------------------------------------------------------------------- */
/*                          INTERFACE POUR OPERANDE RENOMMEE                          */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type d'une interface pour un opérande renommé. */
G_DEFINE_INTERFACE(GRenamedOperand, g_renamed_operand, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de renommage.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_renamed_operand_default_init(GRenamedOperandInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                                                                             *
*  Description : Fournit un texte comme représentation alternative d'opérande.*
*                                                                             *
*  Retour      : Chaîne de caractère de représentation alternative.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_renamed_operand_get_text(const GRenamedOperand *operand)
{
    char *result;                           /* Texte à retourner           */
    GRenamedOperandIface *iface;            /* Interface utilisée          */

    iface = G_RENAMED_OPERAND_GET_IFACE(operand);

    result = iface->get_text(operand);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         INTERFACE POUR OPERANDE RENOMMABLE                         */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type d'une interface pour le renommage d'un opérande. */
G_DEFINE_INTERFACE(GRenameableOperand, g_renameable_operand, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de renommage.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_renameable_operand_default_init(GRenameableOperandInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                text    = texte alternatif de représentation.                *
*                                                                             *
*  Description : Construit un opérande de représentation alternative.         *
*                                                                             *
*  Retour      : Nouvel opérande, en version renommée.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRenamedOperand *g_renameable_operand_build(const GRenameableOperand *operand, const char *text)
{
    GRenamedOperand *result;                /* Instance à retourner        */
    GRenameableOperandIface *iface;         /* Interface utilisée          */

    iface = G_RENAMEABLE_OPERAND_GET_IFACE(operand);

    result = iface->build(operand, text);

    return result;

}
