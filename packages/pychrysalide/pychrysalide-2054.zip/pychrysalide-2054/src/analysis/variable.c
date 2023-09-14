
/* Chrysalide - Outil d'analyse de fichiers binaires
 * variable.c - manipulation des variables en tout genre
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "variable.h"


#include <malloc.h>
#include <stdint.h>
#include <string.h>


#include "types/cse.h"
#include "../common/extstr.h"



/* ------------------- ASSOCIATION D'UN TYPE ET D'UNE DESIGNATION ------------------- */


/* Variable typée (instance) */
struct _GBinVariable
{
    GObject parent;                         /* A laisser en premier        */

    GDataType *type;                        /* Type de la variable         */
    char *name;                             /* Désignation humaine         */

    GDataType *owner;                       /* Zone d'appartenance         */

};

/* Variable typée (classe) */
struct _GBinVariableClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des variables. */
static void g_binary_variable_class_init(GBinVariableClass *);

/* Initialise l'instande d'une variable. */
static void g_binary_variable_init(GBinVariable *);

/* Supprime toutes les références externes. */
static void g_binary_variable_dispose(GBinVariable *);

/* Procède à la libération totale de la mémoire. */
static void g_binary_variable_finalize(GBinVariable *);



/* -------------------- BASE DE VARIABLES OU VARIABLES INCONNUES -------------------- */


/* Base de variable (instance) */
struct _GUnknownVariable
{
    GObject parent;                         /* A laisser en premier        */

    size_t offset;                          /* Position abstraite associée */
    size_t size;                            /* Taille en mémoire           */

};

/* Base de variable (classe) */
struct _GUnknownVariableClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des bases de variables. */
static void g_unknown_variable_class_init(GUnknownVariableClass *);

/* Initialise l'instande d'une base de variable. */
static void g_unknown_variable_init(GUnknownVariable *);



/* ---------------------------------------------------------------------------------- */
/*                     ASSOCIATION D'UN TYPE ET D'UNE DESIGNATION                     */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une base de variable. */
G_DEFINE_TYPE(GBinVariable, g_binary_variable, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des variables.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_variable_class_init(GBinVariableClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_binary_variable_dispose;
    object->finalize = (GObjectFinalizeFunc)g_binary_variable_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise l'instande d'une variable.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_variable_init(GBinVariable *var)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_variable_dispose(GBinVariable *var)
{
    g_clear_object(&var->type);

    g_clear_object(&var->owner);

    G_OBJECT_CLASS(g_binary_variable_parent_class)->dispose(G_OBJECT(var));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_variable_finalize(GBinVariable *var)
{
    if (var->name != NULL)
        free(var->name);

    G_OBJECT_CLASS(g_binary_variable_parent_class)->finalize(G_OBJECT(var));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de la variable à mettre en place.                *
*                                                                             *
*  Description : Crée une représentation de variable de type donné.           *
*                                                                             *
*  Retour      : Variable mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinVariable *g_binary_variable_new(GDataType *type)
{
    GBinVariable *result;               /* Variable à retourner        */

    result = g_object_new(G_TYPE_BIN_VARIABLE, NULL);

    result->type = type;
    ///// A retirer /// g_object_ref(G_OBJECT(type));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = variable à consulter.                                  *
*                                                                             *
*  Description : Fournit le type d'une variable donnée.                       *
*                                                                             *
*  Retour      : Type de la variable.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_binary_variable_get_vtype(const GBinVariable *var)
{
    GDataType *result;                      /* Instance à retourner        */

    result = var->type;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = variable à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom d'une variable donnée.                        *
*                                                                             *
*  Retour      : Nom de la variable ou NULL si non précisé.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_binary_variable_get_name(const GBinVariable *var)
{
    return var->name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var  = variable à consulter.                                 *
*                name = désignation à associer à la variable, voire NULL.     *
*                                                                             *
*  Description : Définit le nom d'une variable donnée.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_variable_set_name(GBinVariable *var, const char *name)
{
    if (var->name != NULL)
        free(var->name);

    if (name == NULL) var->name = NULL;
    else var->name = strdup(name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = variable à consulter.                                  *
*                                                                             *
*  Description : Fournit la zone d'appartenance d'une variable donnée.        *
*                                                                             *
*  Retour      : Zone d'appartenance de la variable ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_binary_variable_get_owner(const GBinVariable *var)
{
    return var->owner;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var   = variable à consulter.                                *
*                owner = type identifiant la zone d'appartenance.             *
*                                                                             *
*  Description : Définit la zone d'appartenance d'une variable donnée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_variable_set_owner(GBinVariable *var, GDataType *owner)
{
    var->owner = owner;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var     = variable à convertir.                              *
*                include = doit-on inclure les espaces de noms ?              *
*                                                                             *
*  Description : Décrit la variable donnée sous forme de caractères.          *
*                                                                             *
*  Retour      : Chaîne à libérer de la mémoire après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_binary_variable_to_string(const GBinVariable *var, bool include)
{
    char *result;                           /* Valeur à retourner          */

    result = g_data_type_to_string(var->type, include);

    if (var->name != NULL)
    {
        if (!(g_data_type_is_pointer(var->type) || g_data_type_is_reference(var->type)))
            result = stradd(result, " ");

        result = stradd(result, var->name);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      BASE DE VARIABLES OU VARIABLES INCONNUES                      */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une base de variable. */
G_DEFINE_TYPE(GUnknownVariable, g_unknown_variable, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bases de variables.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_unknown_variable_class_init(GUnknownVariableClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise l'instande d'une base de variable.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_unknown_variable_init(GUnknownVariable *var)
{
    var->offset = SIZE_MAX;
    var->size = SIZE_MAX;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une représentation de variable de type inconnu.         *
*                                                                             *
*  Retour      : Variable mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GUnknownVariable *g_unknown_variable_new(void)
{
    GUnknownVariable *result;               /* Variable à retourner        */

    result = g_object_new(G_TYPE_UNKNOWN_VARIABLE, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premières informations à consulter.                      *
*                b = secondes informations à consulter.                       *
*                                                                             *
*  Description : Etablit la comparaison ascendante entre deux variables.      *
*                                                                             *
*  Retour      : Bilan : -1 (a < b), 0 (a == b) ou 1 (a > b).                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_unknown_variable_compare(const GUnknownVariable **a, const GUnknownVariable **b)
{
    int result;                             /* Bilan à renvoyer            */

    if ((*a)->offset < (*b)->offset) result = -1;
    else if((*a)->offset > (*b)->offset) result = 1;
    else result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var    = variable à manipuler.                               *
*                offset = position (abstraite ou non) à enregistrer.          *
*                                                                             *
*  Description : Définit la position associée à une variable.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_unknown_variable_set_offset(GUnknownVariable *var, size_t offset)
{
    var->offset = offset;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var = variable à manipuler.                                  *
*                                                                             *
*  Description : Fournit la position associée à une variable.                 *
*                                                                             *
*  Retour      : Position de la variable.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_unknown_variable_get_offset(const GUnknownVariable *var)
{
    return var->offset;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : var    = variable à manipuler.                               *
*                offset = position (abstraite ou non) à traiter.              *
*                                                                             *
*  Description : Indique si une position est contenue dans une variable.      *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_unknown_variable_contains_offset(const GUnknownVariable *var, size_t offset)
{
    bool result;                            /* Bilan à retourner           */

    if (var->offset == SIZE_MAX)
        return false;

    if (var->size == SIZE_MAX)
        result = (var->offset == offset);

    else result = (var->offset <= offset && offset < (var->offset + var->size));

    return result;

}
