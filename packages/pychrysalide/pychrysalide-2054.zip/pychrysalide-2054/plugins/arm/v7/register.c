
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.c - aides auxiliaires relatives aux registres ARMv7
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


#include "register.h"


#include "register-int.h"



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Initialise la classe des registres ARMv7. */
static void g_armv7_register_class_init(GArmV7RegisterClass *);

/* Initialise une instance de registre ARMv7. */
static void g_armv7_register_init(GArmV7Register *);

/* Supprime toutes les références externes. */
static void g_armv7_register_dispose(GArmV7Register *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_register_finalize(GArmV7Register *);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre ARMv7. */
G_DEFINE_TYPE(GArmV7Register, g_armv7_register, G_TYPE_ARM_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres ARMv7.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_register_class_init(GArmV7RegisterClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */

    object_class = G_OBJECT_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_register_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_armv7_register_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre ARMv7.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_register_init(GArmV7Register *reg)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_register_dispose(GArmV7Register *reg)
{
    G_OBJECT_CLASS(g_armv7_register_parent_class)->dispose(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_register_finalize(GArmV7Register *reg)
{
    G_OBJECT_CLASS(g_armv7_register_parent_class)->finalize(G_OBJECT(reg));

}
