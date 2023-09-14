
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.c - prototypes pour la manipulation des routines du format Dex
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "routine.h"


#include <analysis/routine-int.h>



/* Représentation de routine Dex (instance) */
struct _GDexRoutine
{
    GBinRoutine parent;                     /* A laisser en premier        */

    GDexMethod *method;                     /* Lien circulaire !           */

};


/* Représentation de routine Dex (classe) */
struct _GDexRoutineClass
{
    GBinRoutineClass parent;                /* A laisser en premier        */

};



/* Initialise la classe des représentation de routine. */
static void g_dex_routine_class_init(GDexRoutineClass *);

/* Initialise une instance représentation de routine. */
static void g_dex_routine_init(GDexRoutine *);

/* Procède à la libération totale de la mémoire. */
static void g_dex_routine_finalize(GDexRoutine *);

/* Supprime toutes les références externes. */
static void g_dex_routine_dispose(GDexRoutine *);



/* Indique le type défini pour une représentation de routine. */
G_DEFINE_TYPE(GDexRoutine, g_dex_routine, G_TYPE_BIN_ROUTINE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des représentation de routine.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_routine_class_init(GDexRoutineClass *klass)
{
    GObjectClass *object;                   /* Version de base de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dex_routine_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dex_routine_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance représentation de routine.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_routine_init(GDexRoutine *routine)
{
    routine->method = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_routine_dispose(GDexRoutine *routine)
{
    G_OBJECT_CLASS(g_dex_routine_parent_class)->dispose(G_OBJECT(routine));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dex_routine_finalize(GDexRoutine *routine)
{
    G_OBJECT_CLASS(g_dex_routine_parent_class)->finalize(G_OBJECT(routine));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une représentation de routine.                          *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexRoutine *g_dex_routine_new(void)
{
    GDexRoutine *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_DEX_ROUTINE, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier Dex.         *
*                method  = méthode Dex définissant la routine.                *
*                                                                             *
*  Description : Lie une routine à sa méthode Dex d'origine.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_dex_routine_attach_method(GDexRoutine *routine, GDexMethod *method)
{
    routine->method = method;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier Dex.         *
*                                                                             *
*  Description : Fournit la méthode liée à une routine d'origine Dex.         *
*                                                                             *
*  Retour      : Méthode Dex liée à la routine ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDexMethod *g_dex_routine_get_method(const GDexRoutine *routine)
{
    GDexMethod *result;                     /* Méthode à retourner         */

    result = routine->method;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}
