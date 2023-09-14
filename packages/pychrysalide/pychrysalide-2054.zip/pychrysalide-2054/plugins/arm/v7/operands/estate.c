
/* Chrysalide - Outil d'analyse de fichiers binaires
 * estate.c - décalages de valeurs
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "estate.h"


#include <core/columns.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Définition d'un opérande affichant le choix d'un boutisme (instance) */
struct _GArmV7EndianOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

};


/* Définition d'un opérande affichant le choix d'un boutisme (classe) */
struct _GArmV7EndianOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/* Initialise la classe des affichages de boutisme. */
static void g_armv7_endian_operand_class_init(GArmV7EndianOperandClass *);

/* Initialise une instance d'affichage de boutisme. */
static void g_armv7_endian_operand_init(GArmV7EndianOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_endian_operand_dispose(GArmV7EndianOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_endian_operand_finalize(GArmV7EndianOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Traduit un opérande en version humainement lisible. */
static void g_armv7_endian_operand_print(const GArmV7EndianOperand *, GBufferLine *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour une endian de domaine et d'accès. */
G_DEFINE_TYPE(GArmV7EndianOperand, g_armv7_endian_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des affichages de boutisme.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_endian_operand_class_init(GArmV7EndianOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_endian_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_endian_operand_finalize;

    operand->print = (operand_print_fc)g_armv7_endian_operand_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'affichage de boutisme.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_endian_operand_init(GArmV7EndianOperand *operand)
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

static void g_armv7_endian_operand_dispose(GArmV7EndianOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_endian_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_endian_operand_finalize(GArmV7EndianOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_endian_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : big = indication sur le boutisme à représenter.              *
*                                                                             *
*  Description : Crée une représentation de boutisme ARMv7.                   *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_endian_operand_new(bool big)
{
    GArmV7EndianOperand *result;            /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_ENDIAN_OPERAND, NULL);

    if (big)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7ESOF_BIG);

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

static void g_armv7_endian_operand_print(const GArmV7EndianOperand *operand, GBufferLine *line)
{
    if (g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7ESOF_BIG))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "BE", 2, RTT_KEY_WORD, NULL);
    else
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "LE", 2, RTT_KEY_WORD, NULL);

}
