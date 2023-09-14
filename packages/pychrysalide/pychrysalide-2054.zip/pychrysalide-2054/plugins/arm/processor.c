
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - manipulation du processeur ARM
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


#include "processor.h"


#include "processor-int.h"



/* Initialise la classe des registres ARM. */
static void g_arm_processor_class_init(GArmProcessorClass *);

/* Initialise une instance de registre ARM. */
static void g_arm_processor_init(GArmProcessor *);

/* Supprime toutes les références externes. */
static void g_arm_processor_dispose(GArmProcessor *);

/* Procède à la libération totale de la mémoire. */
static void g_arm_processor_finalize(GArmProcessor *);

/* Indique si l'architecture possède un espace virtuel ou non. */
static bool g_arm_processor_has_virtual_space(const GArmProcessor *);



/* Indique le type défini par la GLib pour le processeur ARM. */
G_DEFINE_TYPE(GArmProcessor, g_arm_processor, G_TYPE_ARCH_PROCESSOR);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des processeurs ARM.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_processor_class_init(GArmProcessorClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchProcessorClass *proc;              /* Encore une autre vision...  */

    object_class = G_OBJECT_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_arm_processor_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_arm_processor_finalize;

    proc = G_ARCH_PROCESSOR_CLASS(klass);

    proc->has_vspace = (has_processor_vspace_fc)g_arm_processor_has_virtual_space;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de processeur ARM.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_processor_init(GArmProcessor *proc)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_processor_dispose(GArmProcessor *proc)
{
    G_OBJECT_CLASS(g_arm_processor_parent_class)->dispose(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arm_processor_finalize(GArmProcessor *proc)
{
    G_OBJECT_CLASS(g_arm_processor_parent_class)->finalize(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Indique si l'architecture possède un espace virtuel ou non.  *
*                                                                             *
*  Retour      : true si un espace virtuel existe, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arm_processor_has_virtual_space(const GArmProcessor *proc)
{
    bool result;                            /* Indication à retourner      */

    result = true;

    return result;

}
