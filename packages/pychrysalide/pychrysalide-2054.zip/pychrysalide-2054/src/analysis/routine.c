
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.c - manipulation des prototypes de fonctions et de variables
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>


#include <i18n.h>


#include "routine-int.h"
#include "../arch/instructions/raw.h"
#include "../common/extstr.h"
#include "../core/columns.h"
#include "../core/params.h"
#include "../glibext/gbinarycursor.h"



/* Initialise la classe des représentations de routine. */
static void g_bin_routine_class_init(GBinRoutineClass *);

/* Initialise une instance de représentation de routine. */
static void g_bin_routine_init(GBinRoutine *);

/* Procède à la libération totale de la mémoire. */
static void g_bin_routine_finalize(GBinRoutine *);

/* Supprime toutes les références externes. */
static void g_bin_routine_dispose(GBinRoutine *);

/* Fournit une étiquette pour viser une routine. */
static char *g_binary_routine_get_label(const GBinRoutine *);



/* Indique le type défini pour une représentation de routine. */
G_DEFINE_TYPE(GBinRoutine, g_bin_routine, G_TYPE_BIN_SYMBOL);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des représentations de routine.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bin_routine_class_init(GBinRoutineClass *klass)
{
    GObjectClass *object;                   /* Version de base de la classe*/
    GBinSymbolClass *symbol;                /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_bin_routine_dispose;
    object->finalize = (GObjectFinalizeFunc)g_bin_routine_finalize;

    symbol = G_BIN_SYMBOL_CLASS(klass);

    symbol->get_label = (get_symbol_label_fc)g_binary_routine_get_label;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de représentation de routine.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bin_routine_init(GBinRoutine *routine)
{
    GBinSymbol *symbol;                     /* Autre version de l'instance */

    symbol = G_BIN_SYMBOL(routine);

    g_binary_symbol_set_stype(symbol, STP_ROUTINE);

    routine->ret_type = NULL;

    routine->namespace = NULL;
    routine->ns_sep = NULL;
    routine->name = NULL;
    routine->full_name = NULL;

    routine->args = NULL;
    routine->args_count = 0;

    routine->locals = NULL;
    routine->locals_count = 0;

    routine->blocks = NULL;

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

static void g_bin_routine_dispose(GBinRoutine *routine)
{
    size_t i;                               /* Boucle de parcours          */

    g_clear_object(&routine->ret_type);

    g_clear_object(&routine->namespace);
    g_clear_object(&routine->full_name);

    for (i = 0; i < routine->args_count; i++)
        g_clear_object(&routine->args[i]);

    for (i = 0; i < routine->locals_count; i++)
        g_clear_object(&routine->locals[i]);

    g_clear_object(&routine->blocks);

    G_OBJECT_CLASS(g_bin_routine_parent_class)->dispose(G_OBJECT(routine));

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

static void g_bin_routine_finalize(GBinRoutine *routine)
{
    if (routine->ns_sep != NULL)
        free(routine->ns_sep);

    if (routine->name != NULL)
        free(routine->name);

    if (routine->args != NULL)
        free(routine->args);

    if (routine->locals != NULL)
        free(routine->locals);

    G_OBJECT_CLASS(g_bin_routine_parent_class)->finalize(G_OBJECT(routine));

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

GBinRoutine *g_binary_routine_new(void)
{
    GBinRoutine *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_BIN_ROUTINE, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type mis en place par la future routine.              *
*                                                                             *
*  Description : Crée une représentation de routine construisant une instance.*
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_binary_routine_new_constructor(GDataType *type)
{
    GBinRoutine *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_BIN_ROUTINE, NULL);

    g_binary_routine_set_name(result, g_data_type_to_string(type, true));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à effacer.                                 *
*                                                                             *
*  Description : Supprime une représentation de routine de la mémoire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#if 0 /* FIXME */
void g_binary_routine_finalize(GBinRoutine *routine)
{
    size_t i;                               /* Boucle de parcours          */

    if (routine->ret_type)
        delete_var(routine->ret_type);

    if (routine->name != NULL)
        free(routine->name);

    for (i = 0; i < routine->old_args_count; i++)
        delete_var(routine->args_types[i]);

    free(routine);

}
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                type    = type de routine spécifié.                          *
*                                                                             *
*  Description : Définit le type d'une routine.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_set_type(GBinRoutine *routine, RoutineType type)
{
    routine->type = type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine   = routine à mettre à jour.                         *
*                namespace = instance d'appartenance.                         *
*                sep       = séparateur à utiliser entre les éléments.        *
*                                                                             *
*  Description : Définit le groupe d'appartenance d'une routine donnée.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_set_namespace(GBinRoutine *routine, GDataType *namespace, char *sep)
{
    if (routine->namespace != NULL)
        g_object_unref(G_OBJECT(routine->namespace));

    if (routine->ns_sep != NULL)
        free(routine->ns_sep);

    assert((namespace == NULL && sep == NULL) || (namespace != NULL && sep != NULL));

    routine->namespace = namespace;
    routine->ns_sep = sep;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                                                                             *
*  Description : Fournit le groupe d'appartenance d'une routine donnée.       *
*                                                                             *
*  Retour      : Eventuelle instance d'appartenance ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_binary_routine_get_namespace(const GBinRoutine *routine)
{
    GDataType *result;                      /* Espace à renvoyer           */

    result = routine->namespace;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                name    = désignation humainement lisible.                   *
*                                                                             *
*  Description : Définit le nom humain d'une routine.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Le nom ne doit pas ensuite être libéré par l'appelant !      *
*                                                                             *
******************************************************************************/

void g_binary_routine_set_name(GBinRoutine *routine, char *name)
{
    if (routine->name != NULL)
        free(routine->name);

    routine->name = name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                                                                             *
*  Description : Fournit le nom humain d'une routine.                         *
*                                                                             *
*  Retour      : Désignation humainement lisible ou NULL si non définie.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_binary_routine_get_name(const GBinRoutine *routine)
{
    return routine->name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                type    = désignation complète du nom de la routine.         *
*                                                                             *
*  Description : Définit de façon indirecte le nom humain d'une routine.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_set_typed_name(GBinRoutine *routine, GDataType *type)
{
    if (routine->full_name != NULL)
         g_object_unref(G_OBJECT(routine->full_name));

    routine->full_name = type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                                                                             *
*  Description : Fournit le type construisant le nom humain d'une routine.    *
*                                                                             *
*  Retour      : Eventuel type à l'origine du nom ou NULL.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_binary_routine_get_typed_name(const GBinRoutine *routine)
{
    GDataType *result;                      /* Type à retourner            */

    result = routine->full_name;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                ret     = indication sur le type de retour.                  *
*                                                                             *
*  Description : Définit le type de retour d'une routine.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_set_return_type(GBinRoutine *routine, GDataType *ret)
{
    if (routine->ret_type != NULL)
        g_object_unref(G_OBJECT(routine->ret_type));

    routine->ret_type = ret;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                                                                             *
*  Description : Fournit le type de retour d'une routine.                     *
*                                                                             *
*  Retour      : Indication sur le type de retour en place.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_binary_routine_get_return_type(const GBinRoutine *routine)
{
    GDataType *result;                      /* Type de retour à renvoyer   */

    result = routine->ret_type;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                var     = variable représentant un argument supplémentaire.  *
*                                                                             *
*  Description : Ajoute un argument à une routine.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_add_arg(GBinRoutine *routine, GBinVariable *var)
{
    routine->args = realloc(routine->args, ++routine->args_count * sizeof(GBinVariable *));

    routine->args[routine->args_count - 1] = var;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à consulter.                      *
*                                                                             *
*  Description : Indique le nombre d'arguments associés à une routine.        *
*                                                                             *
*  Retour      : Nombre d'arguments présents.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_binary_routine_get_args_count(const GBinRoutine *routine)
{
    return routine->args_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                index   = indice de l'argument demandé.                      *
*                                                                             *
*  Description : Fournit un argument d'une routine.                           *
*                                                                             *
*  Retour      : Argument demandé.                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinVariable *g_binary_routine_get_arg(const GBinRoutine *routine, size_t index)
{
    GBinVariable *result;                   /* Argument à retourner        */

    assert(index < routine->args_count);

    if (index >= routine->args_count)
        result = NULL;

    else
    {
        result = routine->args[index];

        g_object_ref(G_OBJECT(result));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                index   = indice de l'argument à retirer;                    *
*                                                                             *
*  Description : Retire un argument d'une routine.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_remove_arg(GBinRoutine *routine, size_t index)
{
    g_object_unref(G_OBJECT(routine->args[index]));

    if ((index + 1) < routine->args_count)
        memmove(&routine->args[index], &routine->args[index + 1],
                (routine->args_count - index - 1) * sizeof(GBinVariable *));

    routine->args_count--;

    routine->args = (GBinVariable **)realloc(routine->args,
                                             routine->args_count * sizeof(GBinVariable *));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à manipuler.                               *
*                                                                             *
*  Description : Fournit une étiquette pour viser une routine.                *
*                                                                             *
*  Retour      : Désignation humainement lisible ou NULL si non définie.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_binary_routine_get_label(const GBinRoutine *routine)
{
    char *result;                           /* Etiquette à renvoyer        */
    char *tmp;                              /* Construction temporaire     */

    result = NULL;

    if (routine->namespace != NULL)
    {
        tmp = g_data_type_to_string(routine->namespace, true);

        result = stradd(result, tmp);
        result = stradd(result, routine->ns_sep);

        free(tmp);

    }

    if (routine->full_name != NULL)
    {
        tmp = g_data_type_to_string(routine->full_name, true);

        result = stradd(result, tmp);

        free(tmp);

    }

    else if (routine->name != NULL)
        result = stradd(result, routine->name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                offset  = position abstraite à retrouver.                    *
*                local   = indique le type de variable à manipuler.           *
*                                                                             *
*  Description : S'assure qu'une variable est bien associée à une routine.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_register_if_needed(GBinRoutine *routine, size_t offset, bool local)
{
#if 0 /* FIXME */
    GUnknownVariable ***list;               /* Liste à manipuler           */
    size_t *count;                          /* Taille de la liste          */
    bool found;                             /* Indication de présence      */
    size_t i;                               /* Boucle de parcours          */    
    GUnknownVariable *new;                  /* Nouvelle variable à intégrer*/

    if (local)
    {
        list = &routine->locals;
        count = &routine->locals_count;
    }
    else
    {
        list = &routine->args;
        count = &routine->args_count;
    }

    found = false;

    for (i = 0; i < *count && !found; i++)
        found = g_unknown_variable_contains_offset((*list)[i], offset);

    if (!found)
    {
        /* Construction */

        new = g_unknown_variable_new();

        g_unknown_variable_set_offset(new, offset);

        /* Ajout */

        (*list)= (variable **)realloc(*list, ++(*count) * sizeof(GUnknownVariable *));
        (*list)[*count - 1] = new;

        qsort(*list, *count, sizeof(GUnknownVariable *), g_unknown_variable_compare);


    }
#endif
}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                offset  = position abstraite à retrouver.                    *
*                local   = indique le type de variable à manipuler.           *
*                                                                             *
*  Description : Donne l'indice d'une variable dans la liste d'une routine.   *
*                                                                             *
*  Retour      : Indice de la variable dans la liste adaptée.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_binary_routine_get_var_index_from_offset(const GBinRoutine *routine, size_t offset, bool local)
{
#if 0 /* FIXME */
    size_t result;                          /* Indice à renvoyer           */
    GUnknownVariable ***list;               /* Liste à manipuler           */
    size_t *count;                          /* Taille de la liste          */
    size_t i;                               /* Boucle de parcours          */    

    result = SIZE_MAX;

    if (local)
    {
        list = &routine->locals;
        count = &routine->locals_count;
    }
    else
    {
        list = &routine->args;
        count = &routine->args_count;
    }

    for (i = 0; i < *count && result == SIZE_MAX; i++)
        if (g_unknown_variable_contains_offset((*list)[i], offset))
            result = i;

    return result;
#endif

    return SIZE_MAX;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                                                                             *
*  Description : Fournit les blocs basiques de la routine.                    *
*                                                                             *
*  Retour      : Ensemble de blocs déterminés via les instructions.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBlockList *g_binary_routine_get_basic_blocks(const GBinRoutine *routine)
{
    GBlockList *result;                     /* Instance de liste à renvoyer*/

    result = routine->blocks;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                blocks  = ensemble de blocs déterminés via les instructions. *
*                                                                             *
*  Description : Définit les blocs basiques de la routine.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_routine_set_basic_blocks(GBinRoutine *routine, GBlockList *blocks)
{
    g_clear_object(&routine->blocks);

    g_object_ref(G_OBJECT(blocks));

    routine->blocks = blocks;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                include = doit-on inclure les espaces de noms ?              *
*                                                                             *
*  Description : Décrit le prototype de la routine sous forme de caractères.  *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer de la mémoire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_binary_routine_to_string(const GBinRoutine *routine, bool include)
{
    char *result;                           /* Chaîne à renvoyer           */
    char *namespace;                        /* Groupe d'appartenance       */
    char *name;                             /* Désignation de la routine   */
    size_t i;                               /* Boucle de parcours          */
    char *typestr;                          /* Stockage de nom temporaire  */

    /* Retour de la fonction */

    switch (routine->type)
    {
        case RTT_CONSTRUCTOR:
            result = g_binary_routine_get_label(routine);
            result = stradd(result, " *");
            break;

        case RTT_DESTRUCTOR:
            result = strdup("void ");
            break;

        default: /* Pour gcc */
        case RTT_CLASSIC:
            if (routine->ret_type == NULL) result = strdup("??? ");
            else
            {
                result = g_data_type_to_string(routine->ret_type, include);

                if (!(g_data_type_is_pointer(routine->ret_type) || g_data_type_is_reference(routine->ret_type)))
                    result = stradd(result, " ");

            }
            break;

    }

    /* Nom de la routine */

    if (routine->namespace != NULL)
    {
        namespace = g_data_type_to_string(routine->namespace, include);

        result = stradd(result, namespace);
        result = stradd(result, routine->ns_sep);

        free(namespace);

    }

    if (routine->full_name != NULL)
        name = g_data_type_to_string(routine->full_name, true);

    else if (routine->name != NULL)
        name = routine->name;

    else
        name = NULL;

    if (name != NULL)
    {
        switch (routine->type)
        {
            case RTT_CONSTRUCTOR:
                result = stradd(result, name);
                result = stradd(result, routine->ns_sep);
                result = stradd(result, name);
                break;

            case RTT_DESTRUCTOR:
                result = stradd(result, name);
                result = stradd(result, routine->ns_sep);
                result = stradd(result, "~");
                result = stradd(result, name);
                break;

            default: /* Pour gcc */
            case RTT_CLASSIC:
                result = stradd(result, name);
                break;

        }

    }

    if (routine->full_name != NULL)
        free(name);

    /* Liste des arguments */

    result = stradd(result, "(");

    for (i = 0; i < routine->args_count; i++)
    {
        if (i > 0) result = stradd(result, ", ");

        typestr = g_binary_variable_to_string(routine->args[i], include);
        result = stradd(result, typestr);
        free(typestr);

    }

    result = stradd(result, ")");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à afficher.                                *
*                lang    = langage à utiliser pour la sortie humaine.         *
*                buffer  = tampon mis à disposition pour la sortie.           *
*                                                                             *
*  Description : Procède à l'impression de la description d'une routine.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#if 0
void g_binary_routine_output_info(const GBinRoutine *routine, GLangOutput *lang, GCodeBuffer *buffer)
{
    GBufferLine *line;                      /* Adresse d'une ligne nouvelle*/
    const char *name;                       /* Nom humain de la routine    */
    size_t len;                             /* Taille de ce nom            */
    size_t i;                               /* Boucle de parcours          */

    /* Type de retour */

    line = g_lang_output_start_routine_info(lang, buffer);

    g_data_type_output(routine->ret_type, lang, line, true, false);

    g_buffer_line_append_text(line, DLC_LAST_USED, " ", 1, RTT_COMMENT, NULL);

    /* Nom de la routine */

    name = g_binary_routine_get_name(routine);
    if (name != NULL) len = strlen(name);
    else
    {
        name = "???";
        len = 3;
    }

    g_buffer_line_append_text(line, DLC_LAST_USED, name, len, RTT_COMMENT, NULL);

    /* Arguments éventuels... */

    g_buffer_line_append_text(line, DLC_LAST_USED, "(", 1, RTT_COMMENT, NULL);

    for (i = 0; i < routine->args_count; i++)
    {
        if (i > 0)
            g_buffer_line_append_text(line, DLC_LAST_USED, ", ", 2, RTT_COMMENT, NULL);

        g_binary_variable_output(routine->args[i], lang, line, true, false);

    }

    g_buffer_line_append_text(line, DLC_LAST_USED, ")", 1, RTT_COMMENT, NULL);

    //g_lang_output_end_routine_prototype(lang, buffer, line);

}
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à mettre à jour.                           *
*                lang    = langage à utiliser pour la sortie humaine.         *
*                buffer  = tampon mis à disposition pour la sortie.           *
*                body    = indique le type d'impression attendu.              *
*                                                                             *
*  Description : Procède à l'impression de la décompilation d'une routine.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#if 0
void g_binary_routine_print_code(const GBinRoutine *routine, GLangOutput *lang, GCodeBuffer *buffer, bool body)
{
    GBufferLine *line;                      /* Adresse d'une ligne nouvelle*/
    const char *name;                       /* Nom humain de la routine    */
    size_t len;                             /* Taille de ce nom            */

    /* Type de retour */

    line = g_lang_output_start_routine_prototype(lang, buffer, routine->ret_type);

    g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, " ", 1, RTT_RAW, NULL);

    /* Nom de la routine */

    name = g_binary_routine_get_name(routine);
    if (name != NULL) len = strlen(name);
    else
    {
        name = "???";
        len = 3;
    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, name, len, RTT_COMMENT, NULL);




    /* Corps de la routine ? */

    if (!body)
        g_lang_output_end_routine_prototype(lang, buffer, line);

    else
    {
        g_lang_output_start_routine_body(lang, buffer, line);

        if (routine->dinstr != NULL)
            g_dec_instruction_print(routine->dinstr, buffer, line, lang);

        g_lang_output_end_routine_body(lang, buffer);

    }

}
#endif




#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine à consulter.                               *
*                binary  = informations relatives au binaire chargé.          *
*                                                                             *
*  Description : Construit un petit résumé concis de la routine.              *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_binary_routine_build_tooltip(const GBinRoutine *routine, const GLoadedBinary *binary)
{
    char *result;                           /* Description à retourner     */
    GGenConfig *config;                     /* Configuration à consulter   */
    unsigned int max_calls;                 /* Quantité d'appels à afficher*/
    unsigned int max_strings;               /* Nbre de chaînes à afficher  */
    unsigned int ins_count;                 /* Quantité d'instructions     */
    unsigned int call_count;                /* Quantité d'appels           */
    char *call_info;                        /* Détails des appels          */
    unsigned int string_count;              /* Quantité de chaînes         */
    char *string_info;                      /* Détails des chaînes         */
    GArchProcessor *proc;                   /* Architecture utilisée       */
    GBufferCache *cache;                    /* Tampon de désassemblage     */
    const mrange_t *srange;                 /* Couverture de la routine    */
    instr_iter_t *iter;                     /* Parcours local d'adresses   */
    GArchInstruction *instr;                /* Instruction correspondante  */
    size_t dcount;                          /* Nombre de liens de dest.    */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dest;               /* Instr. visée par une autre  */
    const mrange_t *irange;                 /* Emplacement d'instruction   */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */
    GBufferLine *line;                      /* Ligne présente à l'adresse  */
    char *info;                             /* Ligne d'information créée   */
    size_t blk_count;                       /* Nombre de blocs basiques    */

    result = NULL;

    config = get_main_configuration();

    if (!g_generic_config_get_value(config, MPK_TOOLTIP_MAX_CALLS, &max_calls))
        goto gbrbt_bad_config;

    max_calls++;

    if (!g_generic_config_get_value(config, MPK_TOOLTIP_MAX_STRINGS, &max_strings))
        goto gbrbt_bad_config;

    max_strings++;

    ins_count = 0;

    call_count = 0;
    call_info = NULL;

    string_count = 0;
    string_info = NULL;

    proc = g_loaded_binary_get_processor(binary);
    cache = g_loaded_binary_get_disassembly_cache(binary);

    g_buffer_cache_rlock(cache);

    /* Parcours des instructions */

    srange = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

    iter = g_arch_processor_get_iter_from_address(proc, get_mrange_addr(srange));
    if (iter == NULL) goto gbrbt_no_iter;

    restrict_instruction_iterator(iter, srange);

    for (instr = get_instruction_iterator_current(iter);
         instr != NULL;
         instr = get_instruction_iterator_next(iter))
    {
        ins_count ++;

        /* Appels ou références ? */

        g_arch_instruction_lock_dest(instr);
        dcount = g_arch_instruction_count_destinations(instr);

        for (i = 0; i < dcount; i++)
        {
            dest = g_arch_instruction_get_destination(instr, i);

            switch (dest->type)
            {
                case ILT_CALL:

                    call_count++;

                    if (call_count > max_calls)
                        goto next_dest;

                    if (call_count == max_calls)
                    {
                        call_info = stradd(call_info, "\n ...");
                        goto next_dest;
                    }

                    irange = g_arch_instruction_get_range(instr);

                    cursor = g_binary_cursor_new();
                    g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(irange));

                    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

                    g_object_unref(G_OBJECT(cursor));

                    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

                    line = g_buffer_cache_find_line_by_index(cache, index);

                    if (line != NULL)
                    {
                        info = g_buffer_line_get_text(line, DLC_ASSEMBLY_HEAD, DLC_COUNT, true);
                        g_object_unref(G_OBJECT(line));
                    }

                    else
                        info = NULL;

                    if (call_info != NULL)
                        call_info = stradd(call_info, "\n");

                    if (info != NULL)
                    {
                        call_info = stradd(call_info, " - ");
                        call_info = stradd(call_info, info);
                        free(info);
                    }

                    else
                        call_info = stradd(call_info, " - ???");

                    break;

                case ILT_REF:

                    if (!G_IS_RAW_INSTRUCTION(dest->linked))
                        goto next_dest;

                    if (!g_raw_instruction_is_string(G_RAW_INSTRUCTION(dest->linked)))
                        goto next_dest;

                    string_count++;

                    if (string_count > max_strings)
                        goto next_dest;

                    if (string_count == max_strings)
                    {
                        string_info = stradd(string_info, "\n ...");
                        goto next_dest;
                    }

                    irange = g_arch_instruction_get_range(dest->linked);

                    cursor = g_binary_cursor_new();
                    g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(irange));

                    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

                    g_object_unref(G_OBJECT(cursor));

                    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

                    line = g_buffer_cache_find_line_by_index(cache, index);

                    if (line != NULL)
                    {
                        info = g_buffer_line_get_text(line, DLC_ASSEMBLY, DLC_COUNT, true);
                        g_object_unref(G_OBJECT(line));
                    }

                    else
                        info = NULL;

                    if (string_info != NULL)
                        string_info = stradd(string_info, "\n");

                    if (info != NULL)
                    {
                        string_info = stradd(string_info, " - ");
                        string_info = stradd(string_info, info);
                        free(info);
                    }

                    else
                        string_info = stradd(string_info, " - ???");

                    break;

                default:
                    break;

            }

 next_dest:

            unref_instr_link(dest);

        }

        g_arch_instruction_unlock_dest(instr);

        g_object_unref(G_OBJECT(instr));

    }

    delete_instruction_iterator(iter);

    /* Construction du résumé */

    if (ins_count > 1)
        asprintf(&result, "%u %s, ", ins_count, _("instructions"));
    else
        asprintf(&result, "%u %s, ", ins_count, _("instruction"));

    blk_count = g_block_list_count_blocks(routine->blocks);

    if (blk_count > 1)
        asprintf(&info, "%zu %s", blk_count, _("basic blocks"));
    else
        asprintf(&info, "%zu %s", blk_count, _("basic block"));

    result = stradd(result, info);
    free(info);

    result = stradd(result, "\n");

    if (call_count > 1)
        asprintf(&info, "%u %s, ", call_count, _("calls"));
    else
        asprintf(&info, "%u %s, ", call_count, _("call"));

    result = stradd(result, info);
    free(info);

    if (string_count > 1)
        asprintf(&info, "%u %s", string_count, _("strings"));
    else
        asprintf(&info, "%u %s", string_count, _("string"));

    result = stradd(result, info);
    free(info);

    if (call_count > 0)
    {
        result = stradd(result, "\n\n");
        result = stradd(result, call_count > 1 ? _("Calls:") : _("Call:"));
        result = stradd(result, "\n");

        result = stradd(result, call_info);
        free(call_info);

    }

    if (string_count > 0)
    {
        result = stradd(result, "\n\n");
        result = stradd(result, string_count > 1 ? _("Strings:") : _("String:"));
        result = stradd(result, "\n");

        result = stradd(result, string_info);
        free(string_info);

    }

 gbrbt_no_iter:

    g_buffer_cache_runlock(cache);

    g_object_unref(G_OBJECT(cache));
    g_object_unref(G_OBJECT(proc));

 gbrbt_bad_config:

    return result;

}


#endif
