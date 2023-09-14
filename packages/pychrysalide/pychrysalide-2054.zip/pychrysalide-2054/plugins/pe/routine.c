
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.c - prototypes pour la manipulation des routines du format PE
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


#include "routine.h"


#include <analysis/routine-int.h>



/* ------------------------ SYMBOLES D'UN FORMAT PE EXPORTES ------------------------ */


/* Représentation de routine PE exportée (instance) */
struct _GPeExportedRoutine
{
    GBinRoutine parent;                     /* A laisser en premier        */

    uint16_t ordinal;                       /* Numéro du symbole           */

};


/* Représentation de routine PE exportée (classe) */
struct _GPeExportedRoutineClass
{
    GBinRoutineClass parent;                /* A laisser en premier        */

};


/* Initialise la classe des routine PE exportées. */
static void g_pe_exported_routine_class_init(GPeExportedRoutineClass *);

/* Initialise une instance de routine PE exportée. */
static void g_pe_exported_routine_init(GPeExportedRoutine *);

/* Procède à la libération totale de la mémoire. */
static void g_pe_exported_routine_finalize(GPeExportedRoutine *);

/* Supprime toutes les références externes. */
static void g_pe_exported_routine_dispose(GPeExportedRoutine *);



/* ------------------------ SYMBOLES D'UN FORMAT PE IMPORTES ------------------------ */


/* Représentation de routine PE importée (instance) */
struct _GPeImportedRoutine
{
    GPeExportedRoutine parent;              /* A laisser en premier        */

    char *library;                          /* Bibliothèque de rattachement*/
    size_t index;                           /* Position dans les imports   */

};


/* Représentation de routine PE importée (classe) */
struct _GPeImportedRoutineClass
{
    GPeExportedRoutineClass parent;         /* A laisser en premier        */

};


/* Initialise la classe des routines PE importées. */
static void g_pe_imported_routine_class_init(GPeImportedRoutineClass *);

/* Initialise une instance de routine PE importée. */
static void g_pe_imported_routine_init(GPeImportedRoutine *);

/* Supprime toutes les références externes. */
static void g_pe_imported_routine_dispose(GPeImportedRoutine *);

/* Procède à la libération totale de la mémoire. */
static void g_pe_imported_routine_finalize(GPeImportedRoutine *);



/* ---------------------------------------------------------------------------------- */
/*                          SYMBOLES D'UN FORMAT PE EXPORTES                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation de routine exportée. */
G_DEFINE_TYPE(GPeExportedRoutine, g_pe_exported_routine, G_TYPE_BIN_ROUTINE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des routines PE exportées.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_pe_exported_routine_class_init(GPeExportedRoutineClass *klass)
{
    GObjectClass *object;                   /* Version de base de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_pe_exported_routine_dispose;
    object->finalize = (GObjectFinalizeFunc)g_pe_exported_routine_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de routine PE exportée.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_pe_exported_routine_init(GPeExportedRoutine *routine)
{
    routine->ordinal = UNDEF_PE_ORDINAL;

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

static void g_pe_exported_routine_dispose(GPeExportedRoutine *routine)
{
    G_OBJECT_CLASS(g_pe_exported_routine_parent_class)->dispose(G_OBJECT(routine));

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

static void g_pe_exported_routine_finalize(GPeExportedRoutine *routine)
{
    G_OBJECT_CLASS(g_pe_exported_routine_parent_class)->finalize(G_OBJECT(routine));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation humainement lisible.                      *
*                                                                             *
*  Description : Crée une représentation de routine exportée pour format PE.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPeExportedRoutine *g_pe_exported_routine_new(const char *name)
{
    GPeExportedRoutine *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_PE_EXPORTED_ROUTINE, NULL);

    if (name != NULL)
        g_binary_routine_set_name(G_BIN_ROUTINE(result), strdup(name));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier PE.          *
*                ordinal = indice de symbole à associer à la routine.         *
*                                                                             *
*  Description : Définit l'indice de la routine dans un fichier PE.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_pe_exported_routine_set_ordinal(GPeExportedRoutine *routine, uint16_t ordinal)
{
    routine->ordinal = ordinal;

    g_binary_symbol_set_flag(G_BIN_SYMBOL(routine), PSF_HAS_ORDINAL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier PE.          *
*                                                                             *
*  Description : Fournit l'indice de la routine dans un fichier PE.           *
*                                                                             *
*  Retour      : Numéro de la routine.                                        *
*                                                                             *
*  Remarques   : C'est à l'appelant de s'assurer de la validité du retour.    *
*                                                                             *
******************************************************************************/

uint16_t g_pe_exported_routine_get_ordinal(const GPeExportedRoutine *routine)
{
    uint16_t result;                        /* Indice à retourner          */

     result = routine->ordinal;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          SYMBOLES D'UN FORMAT PE IMPORTES                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation de routine importée. */
G_DEFINE_TYPE(GPeImportedRoutine, g_pe_imported_routine, G_TYPE_PE_EXPORTED_ROUTINE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des routines PE importées.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_pe_imported_routine_class_init(GPeImportedRoutineClass *klass)
{
    GObjectClass *object;                   /* Version de base de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_pe_imported_routine_dispose;
    object->finalize = (GObjectFinalizeFunc)g_pe_imported_routine_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de routine PE importée.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_pe_imported_routine_init(GPeImportedRoutine *routine)
{
    routine->library = NULL;

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

static void g_pe_imported_routine_dispose(GPeImportedRoutine *routine)
{
    G_OBJECT_CLASS(g_pe_imported_routine_parent_class)->dispose(G_OBJECT(routine));

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

static void g_pe_imported_routine_finalize(GPeImportedRoutine *routine)
{
    if (routine->library != NULL)
        free(routine->library);

    G_OBJECT_CLASS(g_pe_imported_routine_parent_class)->finalize(G_OBJECT(routine));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name  = désignation humainement lisible.                     *
*                index = position du symbole dans les importations.           *
*                                                                             *
*  Description : Crée une représentation de routine importée pour format PE.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPeImportedRoutine *g_pe_imported_routine_new(const char *name, size_t index)
{
    GPeImportedRoutine *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_PE_IMPORTED_ROUTINE, NULL);

    if (name != NULL)
        g_binary_routine_set_name(G_BIN_ROUTINE(result), strdup(name));

    result->index = index;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier PE.          *
*                                                                             *
*  Description : Fournit la position du symbole dans les importations.        *
*                                                                             *
*  Retour      : Indice positif ou nul.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_pe_imported_routine_get_index(const GPeImportedRoutine *routine)
{
    size_t result;                          /* Indice à retourner          */

    result = routine->index;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier PE.          *
*                library = désignation d'une bibliothèque Windows.            *
*                                                                             *
*  Description : Définit le fichier DLL visé par une importation de format PE.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_pe_imported_routine_set_library(GPeImportedRoutine *routine, const char *library)
{
    if (routine->library != NULL)
        free(routine->library);

    if (library == NULL)
        routine->library = NULL;

    else
        routine->library = strdup(library);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine ayant pour origine un fichier PE.          *
*                                                                             *
*  Description : Fournit le fichier DLL visé par une importation de format PE.*
*                                                                             *
*  Retour      : Désignation d'une bibliothèque Windows.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_pe_imported_routine_get_library(const GPeImportedRoutine *routine)
{
    char *result;                           /* Bibliothèque à retourner    */

    result = routine->library;

    return result;

}
