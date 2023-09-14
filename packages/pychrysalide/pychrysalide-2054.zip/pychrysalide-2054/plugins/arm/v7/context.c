
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - contexte lié à l'exécution d'un processeur
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


#include "context.h"


#include <assert.h>


#include "../context-int.h"



/* ------------------------ MANIPULATION GLOBALE DU CONTEXTE ------------------------ */


/* Définition d'un contexte pour processeur ARM (instance) */
struct _GArmV7Context
{
    GArmContext parent;                     /* A laisser en premier        */

};


/* Définition d'un contexte pour processeur ARM (classe) */
struct _GArmV7ContextClass
{
    GArmContextClass parent;                /* A laisser en premier        */

};


/* Initialise la classe des contextes de processeur ARM. */
static void g_armv7_context_class_init(GArmV7ContextClass *);

/* Initialise une instance de contexte de processeur ARM. */
static void g_armv7_context_init(GArmV7Context *);

/* Supprime toutes les références externes. */
static void g_armv7_context_dispose(GArmV7Context *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_context_finalize(GArmV7Context *);

/* Ajoute une adresse virtuelle comme point de départ de code. */
static void g_armv7_context_push_drop_point(GArmV7Context *, DisassPriorityLevel, virt_t, va_list);



/* ---------------------------------------------------------------------------------- */
/*                          MANIPULATION GLOBALE DU CONTEXTE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour le contexte de processeur ARM. */
G_DEFINE_TYPE(GArmV7Context, g_armv7_context, G_TYPE_ARM_CONTEXT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de processeur ARM.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_context_class_init(GArmV7ContextClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GProcContextClass *proc;                /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_context_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_context_finalize;

    proc = G_PROC_CONTEXT_CLASS(klass);

    proc->push_point = (push_drop_point_fc)g_armv7_context_push_drop_point;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de contexte de processeur ARM.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_context_init(GArmV7Context *ctx)
{
    GArmContext *base;                      /* Autre version du contexte   */

    base = G_ARM_CONTEXT(ctx);

    base->areas = (disass_arm_area *)calloc(1, sizeof(disass_arm_area));
    base->acount = 1;

    base->areas[0].start = 0;
    base->areas[0].end = (virt_t)-1;
    base->areas[0].marker = AV7IS_ARM;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_context_dispose(GArmV7Context *ctx)
{
    G_OBJECT_CLASS(g_armv7_context_parent_class)->dispose(G_OBJECT(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_context_finalize(GArmV7Context *ctx)
{
    G_OBJECT_CLASS(g_armv7_context_parent_class)->finalize(G_OBJECT(ctx));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un contexte pour l'exécution du processeur ARM.         *
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArmV7Context *g_armv7_context_new(void)
{
    GArmV7Context *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_CONTEXT, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx   = contexte de désassemblage à compléter.               *
*                level = indication de priorité et d'origine de l'adresse.    *
*                addr  = adresse d'un nouveau point de départ à traiter.      *
*                ap    = forme générique d'un encodage à mémoriser.           *
*                                                                             *
*  Description : Ajoute une adresse virtuelle comme point de départ de code.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_context_push_drop_point(GArmV7Context *ctx, DisassPriorityLevel level, virt_t addr, va_list ap)
{
    ArmV7InstrSet marker;                   /* Type de jeu d'instructions  */

    switch (level)
    {
        case DPL_ENTRY_POINT:
        case DPL_FORMAT_POINT:
        case DPL_SYMBOL:

            if (addr & 0x1)
            {
                addr -= 0x1;
                marker = AV7IS_THUMB;
            }
            else
                marker = AV7IS_ARM;

            break;

        default:

            /**
             * Les messages de GCC annoncent parfois les choses très clairement :
             *
             * context.c:233:33: warning: 'ArmV7InstrSet' is promoted to 'int' when passed through '...'
             *              marker = va_arg(ap, ArmV7InstrSet);
             *                                  ^
             * context.c:233:33: note: (so you should pass 'int' not 'ArmV7InstrSet' to 'va_arg')
             * context.c:233:33: note: if this code is reached, the program will abort
             *
             */

            marker = (ArmV7InstrSet)va_arg(ap, unsigned int);

            /**
             * Attention : toute adresse impaire est destinée à du mode Thumb.
             *
             * Mais la réciproque n'est pas vraie : le mode Thumb peut aussi
             * manipuler des adresses paires.
             */
            assert(((addr & 0x1) && marker == AV7IS_THUMB) || (addr & 0x1) == 0);

            addr &= ~0x1;

            break;

    }

    g_armv7_context_define_encoding(ctx, addr, marker);

    G_PROC_CONTEXT_CLASS(g_armv7_context_parent_class)->push_point(G_PROC_CONTEXT(ctx), level, addr, ap);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx    = contexte de désassemblage à compléter.              *
*                addr   = adresse d'un nouveau point de départ à créer.       *
*                marker = forme générique d'un encodage à mémoriser.          *
*                                                                             *
*  Description : Enregistre l'encodage (générique) utilisé à une adresse.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_armv7_context_define_encoding(GArmV7Context *ctx, virt_t addr, ArmV7InstrSet marker)
{
    _g_arm_context_define_encoding(G_ARM_CONTEXT(ctx), addr, marker);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx  = contexte de désassemblage à consulter.                *
*                addr = adresse d'un nouveau point de départ à retrouver.     *
*                                                                             *
*  Description : Indique l'encodage (générique) utilisé à une adresse donnée. *
*                                                                             *
*  Retour      : Marqueur à priori toujours valide.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ArmV7InstrSet g_armv7_context_find_encoding(GArmV7Context *ctx, virt_t addr)
{
    return (ArmV7InstrSet)_g_arm_context_find_encoding(G_ARM_CONTEXT(ctx), addr);

}
