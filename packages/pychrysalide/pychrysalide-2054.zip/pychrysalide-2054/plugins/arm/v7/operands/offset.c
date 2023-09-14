
/* Chrysalide - Outil d'analyse de fichiers binaires
 * offset.c - constitution d'un décalage positif ou négatif
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


#include "offset.h"


#include <assert.h>
#include <stdio.h>
#include <string.h>


#include <core/columns.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Définition d'un opérande visant à constituer un décalage relatif ARMv7 (instance) */
struct _GArmV7OffsetOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

    GArchOperand *value;                    /* Valeur du décalage          */

};


/* Définition d'un opérande visant à constituer un décalage relatif ARMv7 (classe) */
struct _GArmV7OffsetOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/* Initialise la classe des décalages relatifs ARMv7. */
static void g_armv7_offset_operand_class_init(GArmV7OffsetOperandClass *);

/* Initialise une instance de décalage relatif ARMv7. */
static void g_armv7_offset_operand_init(GArmV7OffsetOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_offset_operand_dispose(GArmV7OffsetOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_offset_operand_finalize(GArmV7OffsetOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_offset_operand_compare(const GArmV7OffsetOperand *, const GArmV7OffsetOperand *, bool);

/* Détermine le chemin conduisant à un opérande interne. */
static char *g_armv7_offset_operand_find_inner_operand_path(const GArmV7OffsetOperand *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
static GArchOperand *g_armv7_offset_operand_get_inner_operand_from_path(const GArmV7OffsetOperand *, const char *);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_offset_operand_print(const GArmV7OffsetOperand *, GBufferLine *);

/* Fournit une liste de candidats embarqués par un candidat. */
static GArchOperand **g_armv7_offset_operand_list_inner_instances(const GArmV7OffsetOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
static void g_armv7_offset_operand_update_inner_instances(GArmV7OffsetOperand *, GArchOperand **, size_t);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un décalage relatif ARMv7. */
G_DEFINE_TYPE(GArmV7OffsetOperand, g_armv7_offset_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des décalages relatifs ARMv7.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_offset_operand_class_init(GArmV7OffsetOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_offset_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_offset_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_armv7_offset_operand_compare;
    operand->find_inner = (find_inner_operand_fc)g_armv7_offset_operand_find_inner_operand_path;
    operand->get_inner = (get_inner_operand_fc)g_armv7_offset_operand_get_inner_operand_from_path;

    operand->print = (operand_print_fc)g_armv7_offset_operand_print;

    operand->list_inner = (operand_list_inners_fc)g_armv7_offset_operand_list_inner_instances;
    operand->update_inner = (operand_update_inners_fc)g_armv7_offset_operand_update_inner_instances;

    operand->load = g_arch_operand_load_generic_fixed_1;
    operand->store = g_arch_operand_store_generic_fixed;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de décalage relatif ARMv7.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_offset_operand_init(GArmV7OffsetOperand *operand)
{
    operand->value = NULL;

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

static void g_armv7_offset_operand_dispose(GArmV7OffsetOperand *operand)
{
    g_clear_object(&operand->value);

    G_OBJECT_CLASS(g_armv7_offset_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_offset_operand_finalize(GArmV7OffsetOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_offset_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : positive = indique si la quantité doit être ajoutée ou non.  *
*                value    = valeur du décalage à appliquer.                   *
*                                                                             *
*  Description : Crée un décalage selon un sens et une valeur donnés.         *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_offset_operand_new(bool positive, GArchOperand *value)
{
    GArmV7OffsetOperand *result;            /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_OFFSET_OPERAND, NULL);

    if (positive)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7OOF_POSITIVE);

    result->value = value;

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Founit la valeur utilisée pour un décalage.                  *
*                                                                             *
*  Retour      : Opérande en place.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_offset_operand_get_value(const GArmV7OffsetOperand *operand)
{
    GArchOperand *result;                   /* Instance à retourner        */

    result = operand->value;

    g_object_ref(G_OBJECT(result));

    return result;

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

static int g_armv7_offset_operand_compare(const GArmV7OffsetOperand *a, const GArmV7OffsetOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    result = g_arch_operand_compare(a->value, b->value);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_offset_operand_parent_class);
        result = class->compare(G_ARCH_OPERAND(a), G_ARCH_OPERAND(b), false);
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

static char *g_armv7_offset_operand_find_inner_operand_path(const GArmV7OffsetOperand *operand, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */

    if (target == operand->value)
        result = strdup("0");
    else
        result = NULL;

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

static GArchOperand *g_armv7_offset_operand_get_inner_operand_from_path(const GArmV7OffsetOperand *operand, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */

    result = NULL;

    if (strncmp(path, "0", 1) == 0)
        switch (path[1])
        {
            case '\0':
                result = operand->value;
                g_object_ref(G_OBJECT(result));
                break;

            case ':':
                result = g_arch_operand_get_inner_operand_from_path(operand->value, path + 1);
                break;

        }

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

static void g_armv7_offset_operand_print(const GArmV7OffsetOperand *operand, GBufferLine *line)
{
    if (!g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7OOF_POSITIVE))
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "-", 1, RTT_KEY_WORD, NULL);

    g_arch_operand_print(operand->value, line);

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

static GArchOperand **g_armv7_offset_operand_list_inner_instances(const GArmV7OffsetOperand *operand, size_t *count)
{
    GArchOperand **result;                  /* Instances à retourner       */

    *count = 1;

    result = malloc(*count * sizeof(GArchOperand *));

    result[0] = operand->value;
    g_object_ref(G_OBJECT(result[0]));

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

static void g_armv7_offset_operand_update_inner_instances(GArmV7OffsetOperand *operand, GArchOperand **instances, size_t count)
{
    assert(count == 1);

    g_clear_object(&operand->value);

    operand->value = instances[0];
    g_object_ref(G_OBJECT(instances[0]));

}
