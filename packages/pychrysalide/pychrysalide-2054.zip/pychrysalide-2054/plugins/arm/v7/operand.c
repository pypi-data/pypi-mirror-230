
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.c - opérandes ARMv7
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "operand.h"


#include "operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Initialise la classe des affichages de boutisme. */
static void g_armv7_operand_class_init(GArmV7OperandClass *);

/* Initialise une instance d'affichage de boutisme. */
static void g_armv7_operand_init(GArmV7Operand *);

/* Supprime toutes les références externes. */
static void g_armv7_operand_dispose(GArmV7Operand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_operand_finalize(GArmV7Operand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_operand_hash(const GArmV7Operand *, bool);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour une  de domaine et d'accès. */
G_DEFINE_TYPE(GArmV7Operand, g_armv7_operand, G_TYPE_ARCH_OPERAND);


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

static void g_armv7_operand_class_init(GArmV7OperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->hash = (operand_hash_fc)g_armv7_operand_hash;

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

static void g_armv7_operand_init(GArmV7Operand *operand)
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

static void g_armv7_operand_dispose(GArmV7Operand *operand)
{
    G_OBJECT_CLASS(g_armv7_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_operand_finalize(GArmV7Operand *operand)
{
    G_OBJECT_CLASS(g_armv7_operand_parent_class)->finalize(G_OBJECT(operand));

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                lock    = précise le besoin en verrouillage.                 *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_armv7_operand_hash(const GArmV7Operand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    operand_extra_data_t *extra;            /* Données insérées à modifier */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    if (lock)
        UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}
