
/* Chrysalide - Outil d'analyse de fichiers binaires
 * args.c - listes d'opérandes rassemblées en arguments
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


#include "args.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>


#include <arch/operand-int.h>
#include <common/sort.h>
#include <core/columns.h>
#include <core/logs.h>



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Définition d'un opérande visant une liste d'opérandes Dalvik (instance) */
struct _GDalvikArgsOperand
{
    GArchOperand parent;                    /* Instance parente            */

    GArchOperand **args;                    /* Liste d'arguments           */
    size_t count;                           /* Taille de cette liste       */

};


/* Définition d'un opérande visant une liste d'opérandes Dalvik (classe) */
struct _GDalvikArgsOperandClass
{
    GArchOperandClass parent;               /* Classe parente              */

};


/* Initialise la classe des listes d'opérandes Dalvik. */
static void g_dalvik_args_operand_class_init(GDalvikArgsOperandClass *);

/* Initialise une instance de liste d'opérandes Dalvik. */
static void g_dalvik_args_operand_init(GDalvikArgsOperand *);

/* Supprime toutes les références externes. */
static void g_dalvik_args_operand_dispose(GDalvikArgsOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_args_operand_finalize(GDalvikArgsOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_dalvik_args_operand_compare(const GDalvikArgsOperand *, const GDalvikArgsOperand *, bool);

/* Détermine le chemin conduisant à un opérande interne. */
static char *g_dalvik_args_operand_find_inner_operand_path(const GDalvikArgsOperand *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
static GArchOperand *g_dalvik_args_operand_get_inner_operand_from_path(const GDalvikArgsOperand *, const char *);

/* Traduit un opérande en version humainement lisible. */
static void g_dalvik_args_operand_print(const GDalvikArgsOperand *, GBufferLine *);

/* Fournit une liste de candidats embarqués par un candidat. */
static GArchOperand **g_dalvik_args_operand_list_inner_instances(const GDalvikArgsOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
static void g_dalvik_args_operand_update_inner_instances(GDalvikArgsOperand *, GArchOperand **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_dalvik_args_operand_hash(const GDalvikArgsOperand *, bool);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour une liste d'arguments Dalvik. */
G_DEFINE_TYPE(GDalvikArgsOperand, g_dalvik_args_operand, G_TYPE_ARCH_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des listes d'opérandes Dalvik.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_args_operand_class_init(GDalvikArgsOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_args_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_args_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_dalvik_args_operand_compare;
    operand->find_inner = (find_inner_operand_fc)g_dalvik_args_operand_find_inner_operand_path;
    operand->get_inner = (get_inner_operand_fc)g_dalvik_args_operand_get_inner_operand_from_path;

    operand->print = (operand_print_fc)g_dalvik_args_operand_print;

    operand->list_inner = (operand_list_inners_fc)g_dalvik_args_operand_list_inner_instances;
    operand->update_inner = (operand_update_inners_fc)g_dalvik_args_operand_update_inner_instances;
    operand->hash = (operand_hash_fc)g_dalvik_args_operand_hash;

    operand->load = g_arch_operand_load_generic_variadic;
    operand->store = g_arch_operand_store_generic_variadic;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de liste d'opérandes Dalvik.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_args_operand_init(GDalvikArgsOperand *operand)
{
    operand->args = NULL;
    operand->count = 0;

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

static void g_dalvik_args_operand_dispose(GDalvikArgsOperand *operand)
{
    size_t i;

    for (i = 0; i < operand->count; i++)
        g_clear_object(&operand->args[i]);

    G_OBJECT_CLASS(g_dalvik_args_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_dalvik_args_operand_finalize(GDalvikArgsOperand *operand)
{
    if (operand->args != NULL)
        free(operand->args);

    G_OBJECT_CLASS(g_dalvik_args_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un réceptacle pour opérandes Dalvik servant d'arguments.*
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_dalvik_args_operand_new(void)
{
    GArchOperand *result;                   /* Structure à retourner       */

    result = g_object_new(G_TYPE_DALVIK_ARGS_OPERAND, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à compléter.                              *
*                arg     = nouvel argument pour un appel.                     *
*                                                                             *
*  Description : Ajoute un élément à la liste d'arguments Dalvik.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_dalvik_args_operand_add(GDalvikArgsOperand *operand, GArchOperand *arg)
{
    operand->count++;
    operand->args = realloc(operand->args, operand->count * sizeof(GArchOperand *));

    operand->args[operand->count - 1] = arg;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à compléter.                              *
*                                                                             *
*  Description : Fournit le nombre d'arguments pris en charge.                *
*                                                                             *
*  Retour      : Nombre positif ou nul.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_dalvik_args_count(const GDalvikArgsOperand *operand)
{
    return operand->count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à compléter.                              *
*                index   = indice de l'argument recherché.                    *
*                                                                             *
*  Description : Founit un élément de la liste d'arguments Dalvik.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_dalvik_args_operand_get(const GDalvikArgsOperand *operand, size_t index)
{
    assert(index < operand->count);

    return operand->args[index];

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a    = premier opérande à consulter.                         *
*                b    = second opérande à consulter.                          *
*                lock = précise le besoin en verrouillage.                    *
*                                                                             *
*  Description : Compare un opérande avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_dalvik_args_operand_compare(const GDalvikArgsOperand *a, const GDalvikArgsOperand *b, bool lock)
{
    int result;                             /* Bilan à renvoyer            */
    operand_extra_data_t *ea;               /* Données insérées à consulter*/
    operand_extra_data_t *eb;               /* Données insérées à consulter*/
    size_t i;                               /* Boucle de parcours          */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    /* Création de l'objet... */
    if (b == NULL)
        result = 1;

    else
    {
        ea = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(a));
        eb = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(b));

        if (lock)
        {
            LOCK_GOBJECT_EXTRA(ea);
            LOCK_GOBJECT_EXTRA(eb);
        }

        result = sort_unsigned_long(a->count, b->count);

        for (i = 0; i < a->count && result == 0; i++)
            result = g_arch_operand_compare(a->args[i], b->args[i]);

        if (result == 0)
        {
            class = G_ARCH_OPERAND_CLASS(g_dalvik_args_operand_parent_class);
            result = class->compare(G_ARCH_OPERAND(a), G_ARCH_OPERAND(b), false);
        }

        if (lock)
        {
            UNLOCK_GOBJECT_EXTRA(eb);
            UNLOCK_GOBJECT_EXTRA(ea);
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                target  = instruction à venir retrouver.                     *
*                                                                             *
*  Description : Détermine le chemin conduisant à un opérande interne.        *
*                                                                             *
*  Retour      : Chemin d'accès à l'opérande ou NULL en cas d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_dalvik_args_operand_find_inner_operand_path(const GDalvikArgsOperand *operand, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */
    size_t i;                               /* Boucle de parcours          */
    int ret;                                /* Bilan d'une construction    */
    char *sub_path;                         /* Sous-chemin emprunté        */

    result = NULL;

    /* Première passe : accès direct */

    for (i = 0; i < operand->count && result == NULL; i++)
    {
        if (operand->args[i] == target)
        {
            ret = asprintf(&result, "%zu", i);
            if (ret == -1)
            {
                LOG_ERROR_N("asprintf");
                result = NULL;
            }
        }

    }

    /* Seconde passe : accès profond */

    for (i = 0; i < operand->count && result == NULL; i++)
    {
        sub_path = g_arch_operand_find_inner_operand_path(operand->args[i], target);

        if (sub_path != NULL)
        {
            ret = asprintf(&result, "%zu:%s", i, sub_path);
            if (ret == -1)
            {
                LOG_ERROR_N("asprintf");
                result = NULL;
            }

            free(sub_path);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                path  = chemin d'accès à un opérande à retrouver.            *
*                                                                             *
*  Description : Obtient l'opérande correspondant à un chemin donné.          *
*                                                                             *
*  Retour      : Opérande trouvé ou NULL en cas d'échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchOperand *g_dalvik_args_operand_get_inner_operand_from_path(const GDalvikArgsOperand *operand, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */
    size_t index;                           /* Indice de l'opérande visé   */
    char *end;                              /* Poursuite du parcours ?     */
    GArchOperand *found;                    /* Opérande trouvé             */

    result = NULL;

    /* Recherche au premier niveau */

    index = strtoul(path, &end, 10);

    if ((index == ULONG_MAX && errno == ERANGE) || (index == 0 && errno == EINVAL))
    {
        LOG_ERROR_N("strtoul");
        goto done;
    }

    if (index >= operand->count)
        goto done;

    found = operand->args[index];
    if (found == NULL) goto done;

    if (*end == '\0')
    {
        result = found;
        g_object_ref(G_OBJECT(result));
        goto done;
    }

    /* Recherche en profondeur */

    assert(*end == ':');

    result = g_arch_operand_get_inner_operand_from_path(found, end + 1);

 done:

    return result;

}


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

static void g_dalvik_args_operand_print(const GDalvikArgsOperand *operand, GBufferLine *line)
{
    size_t i;                               /* Boucle de parcours          */

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "{", 1, RTT_HOOK, NULL);

    if (operand->count > 0)
    {
        g_arch_operand_print(operand->args[0], line);

        for (i = 1; i < operand->count; i++)
        {
            g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
            g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);

            g_arch_operand_print(operand->args[i], line);

        }

    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "}", 1, RTT_HOOK, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                count   = quantité d'instances à l'unicité internes.         *
*                                                                             *
*  Description : Fournit une liste de candidats embarqués par un candidat.    *
*                                                                             *
*  Retour      : Liste de candidats internes ou NULL si aucun.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchOperand **g_dalvik_args_operand_list_inner_instances(const GDalvikArgsOperand *operand, size_t *count)
{
    GArchOperand **result;                  /* Instances à retourner       */
    size_t i;                               /* Boucle de parcours          */

    *count = operand->count;

    result = malloc(*count * sizeof(GArchOperand *));

    for (i = 0; i < *count; i++)
    {
        result[i] = operand->args[i];
        g_object_ref(G_OBJECT(result[i]));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand   = objet dont l'instance se veut unique.            *
*                instances = liste de candidats internes devenus singletons.  *
*                count     = quantité d'instances à l'unicité internes.       *
*                                                                             *
*  Description : Met à jour une liste de candidats embarqués par un candidat. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_args_operand_update_inner_instances(GDalvikArgsOperand *operand, GArchOperand **instances, size_t count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < count; i++)
        g_object_unref(G_OBJECT(operand->args[i]));

    operand->count = count;
    operand->args = realloc(operand->args, operand->count * sizeof(GArchOperand *));

    for (i = 0; i < count; i++)
    {
        operand->args[i] = instances[i];
        g_object_ref(G_OBJECT(instances[i]));
    }

}


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

static guint g_dalvik_args_operand_hash(const GDalvikArgsOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    operand_extra_data_t *extra;            /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_dalvik_args_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= operand->count;

    if (lock)
        UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}
