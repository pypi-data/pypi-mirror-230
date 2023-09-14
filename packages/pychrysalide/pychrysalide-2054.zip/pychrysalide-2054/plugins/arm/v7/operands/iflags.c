
/* Chrysalide - Outil d'analyse de fichiers binaires
 * iflags.c - opérandes précisant un masque d'interruption ARMv7
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


#include "iflags.h"


#include <core/columns.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Définition d'un opérande précisant un masque d'interruption ARMv7 (instance) */
struct _GArmV7IFlagsOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

};


/* Définition d'un opérande précisant un masque d'interruption ARMv7 (classe) */
struct _GArmV7IFlagsOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/* Initialise la classe des opérandes de masque d'interruption. */
static void g_armv7_iflags_operand_class_init(GArmV7IFlagsOperandClass *);

/* Initialise une instance d'opérande de masque d'interruption. */
static void g_armv7_iflags_operand_init(GArmV7IFlagsOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_iflags_operand_dispose(GArmV7IFlagsOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_iflags_operand_finalize(GArmV7IFlagsOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_iflags_operand_print(const GArmV7IFlagsOperand *, GBufferLine *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un opérande de masque d'interruption ARMv7. */
G_DEFINE_TYPE(GArmV7IFlagsOperand, g_armv7_iflags_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes de masque d'interruption. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_iflags_operand_class_init(GArmV7IFlagsOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_iflags_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_iflags_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->print = (operand_print_fc)g_armv7_iflags_operand_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande de masque d'interruption. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_iflags_operand_init(GArmV7IFlagsOperand *operand)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_iflags_operand_dispose(GArmV7IFlagsOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_iflags_operand_parent_class)->dispose(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_iflags_operand_finalize(GArmV7IFlagsOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_iflags_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = bit d'arrêt asynchrone.                                  *
*                i = bit d'interruption IRQ.                                  *
*                f = bit d'interruption FIQ.                                  *
*                                                                             *
*  Description : Crée un opérande de masque d'interruption ARMv7.             *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_iflags_operand_new(bool a, bool i, bool f)
{
    GArmV7IFlagsOperand *result;         /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_IFLAGS_OPERAND, NULL);

    if (a)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7IFOF_ABORT);

    if (i)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7IFOF_IRQ);

    if (f)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7IFOF_FIQ);

    return G_ARCH_OPERAND(result);

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à traiter.                                *
*                line    = ligne tampon où imprimer l'opérande donné.         *
*                                                                             *
*  Description : Traduit un opérande en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_iflags_operand_print(const GArmV7IFlagsOperand *operand, GBufferLine *line)
{
    if (g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7IFOF_ABORT))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "A", 1, RTT_REGISTER, NULL);

    if (g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7IFOF_IRQ))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "I", 1, RTT_REGISTER, NULL);

    if (g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7IFOF_FIQ))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "F", 1, RTT_REGISTER, NULL);

}
