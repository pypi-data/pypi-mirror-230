
/* Chrysalide - Outil d'analyse de fichiers binaires
 * maccess.c - accès à la mémorie à partir d'un registre et d'un décalage
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


#include "maccess.h"


#include <assert.h>
#include <stdio.h>
#include <stdlib.h>


#include <common/cpp.h>
#include <core/columns.h>
#include <core/logs.h>


#include "../operand-int.h"



/* -------------------------- DEFINITION D'UN NOUVEAU TYPE -------------------------- */


/* Définition d'un opérande offrant un accès à la mémoire depuis une base (instance) */
struct _GArmV7MAccessOperand
{
    GArmV7Operand parent;                   /* Instance parente            */

    GArchOperand *base;                     /* Base de l'accès en mémoire  */
    GArchOperand *offset;                   /* Décalage pour l'adresse     */
    GArchOperand *shift;                    /* Décalage supplémentaire ?   */

};


/* Définition d'un opérande offrant un accès à la mémoire depuis une base (classe) */
struct _GArmV7MAccessOperandClass
{
    GArmV7OperandClass parent;              /* Classe parente              */

};


/* Initialise la classe des accès à la mémoire chez ARM. */
static void g_armv7_maccess_operand_class_init(GArmV7MAccessOperandClass *);

/* Initialise une instance d'accès à la mémoire chez ARM. */
static void g_armv7_maccess_operand_init(GArmV7MAccessOperand *);

/* Supprime toutes les références externes. */
static void g_armv7_maccess_operand_dispose(GArmV7MAccessOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_maccess_operand_finalize(GArmV7MAccessOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_armv7_maccess_operand_compare(const GArmV7MAccessOperand *, const GArmV7MAccessOperand *, bool);

/* Détermine le chemin conduisant à un opérande interne. */
static char *g_armv7_maccess_operand_find_inner_operand_path(const GArmV7MAccessOperand *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
static GArchOperand *g_armv7_maccess_operand_get_inner_operand_from_path(const GArmV7MAccessOperand *, const char *);

/* Traduit un opérande en version humainement lisible. */
static void g_armv7_maccess_operand_print(const GArmV7MAccessOperand *, GBufferLine *);

/* Fournit une liste de candidats embarqués par un candidat. */
static GArchOperand **g_armv7_maccess_operand_list_inner_instances(const GArmV7MAccessOperand *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
static void g_armv7_maccess_operand_update_inner_instances(GArmV7MAccessOperand *, GArchOperand **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_armv7_maccess_operand_hash(const GArmV7MAccessOperand *, bool);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN NOUVEAU TYPE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un accès à la mémoire depuis une base. */
G_DEFINE_TYPE(GArmV7MAccessOperand, g_armv7_maccess_operand, G_TYPE_ARMV7_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des accès à la mémoire chez ARM.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_maccess_operand_class_init(GArmV7MAccessOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_maccess_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_maccess_operand_finalize;

    operand = G_ARCH_OPERAND_CLASS(klass);

    operand->compare = (operand_compare_fc)g_armv7_maccess_operand_compare;
    operand->find_inner = (find_inner_operand_fc)g_armv7_maccess_operand_find_inner_operand_path;
    operand->get_inner = (get_inner_operand_fc)g_armv7_maccess_operand_get_inner_operand_from_path;

    operand->print = (operand_print_fc)g_armv7_maccess_operand_print;

    operand->list_inner = (operand_list_inners_fc)g_armv7_maccess_operand_list_inner_instances;
    operand->update_inner = (operand_update_inners_fc)g_armv7_maccess_operand_update_inner_instances;
    operand->hash = (operand_hash_fc)g_armv7_maccess_operand_hash;

    operand->load = g_arch_operand_load_generic_fixed_3;
    operand->store = g_arch_operand_store_generic_fixed;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'accès à la mémoire chez ARM.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_maccess_operand_init(GArmV7MAccessOperand *operand)
{
    operand->base = NULL;
    operand->offset = NULL;
    operand->shift = NULL;

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

static void g_armv7_maccess_operand_dispose(GArmV7MAccessOperand *operand)
{
    g_clear_object(&operand->base);
    g_clear_object(&operand->offset);
    g_clear_object(&operand->shift);

    G_OBJECT_CLASS(g_armv7_maccess_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_armv7_maccess_operand_finalize(GArmV7MAccessOperand *operand)
{
    G_OBJECT_CLASS(g_armv7_maccess_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base   = représente le registre de la base d'accès.          *
*                offset = détermine le décalage entre l'adresse et la base.   *
*                shift  = opération de décalage pour jouer sur le décalage.   *
*                post   = précise la forme donnée au décalage à appliquer.    *
*                wback  = indique une mise à jour de la base après usage.     *
*                                                                             *
*  Description : Crée un accès à la mémoire depuis une base et un décalage.   *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_maccess_operand_new(GArchOperand *base, GArchOperand *offset, GArchOperand *shift, bool post, bool wback)
{
    GArmV7MAccessOperand *result;           /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_MACCESS_OPERAND, NULL);

    result->base = base;
    result->offset = offset;
    result->shift = shift;

    if (post)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7MAOF_POST_INDEXED);

    if (wback)
        g_arch_operand_set_flag(G_ARCH_OPERAND(result), A7MAOF_WRITE_BACK);

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Founit la base d'un accès à la mémoire.                      *
*                                                                             *
*  Retour      : Opérande en place.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_maccess_operand_get_base(const GArmV7MAccessOperand *operand)
{
    return operand->base;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Founit le décalage d'un accès à la mémoire depuis la base.   *
*                                                                             *
*  Retour      : Opérande en place.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_maccess_operand_get_offset(const GArmV7MAccessOperand *operand)
{
    return operand->offset;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                                                                             *
*  Description : Founit le décalage d'un décalage pour un accès mémoire.      *
*                                                                             *
*  Retour      : Opérande en place.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_armv7_maccess_operand_get_shift(const GArmV7MAccessOperand *operand)
{
    return operand->shift;

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

static int g_armv7_maccess_operand_compare(const GArmV7MAccessOperand *a, const GArmV7MAccessOperand *b, bool lock)
{
    int result;                             /* Bilan à faire remonter      */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    result = g_arch_operand_compare(a->base, b->base);

    if (result)
        result = g_arch_operand_compare(a->offset, b->offset);

    if (result)
        result = g_arch_operand_compare(a->shift, b->shift);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_armv7_maccess_operand_parent_class);
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

static char *g_armv7_maccess_operand_find_inner_operand_path(const GArmV7MAccessOperand *operand, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */
    size_t count;                           /* Nombre d'opérandes en place */
    size_t i;                               /* Boucle de parcours          */
    int ret;                                /* Bilan d'une construction    */
    char *sub_path;                         /* Sous-chemin emprunté        */

    GArchOperand *candidates[] = { operand->base, operand->offset, operand->shift };

    result = NULL;

    count = ARRAY_SIZE(candidates);

    /* Première passe : accès direct */

    for (i = 0; i < count && result == NULL; i++)
    {
        if (candidates[i] == NULL)
            continue;

        if (candidates[i] == target)
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

    for (i = 0; i < count && result == NULL; i++)
    {
        if (candidates[i] == NULL)
            continue;

        sub_path = g_arch_operand_find_inner_operand_path(candidates[i], target);

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

static GArchOperand *g_armv7_maccess_operand_get_inner_operand_from_path(const GArmV7MAccessOperand *operand, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */
    size_t index;                           /* Indice de l'opérande visé   */
    char *end;                              /* Poursuite du parcours ?     */
    GArchOperand *found;                    /* Opérande trouvé             */

    GArchOperand *candidates[] = { operand->base, operand->offset, operand->shift };

    result = NULL;

    /* Recherche au premier niveau */

    index = strtoul(path, &end, 10);

    if ((index == ULONG_MAX && errno == ERANGE) || (index == 0 && errno == EINVAL))
    {
        LOG_ERROR_N("strtoul");
        goto done;
    }

    if (index >= ARRAY_SIZE(candidates))
        goto done;

    found = candidates[index];
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

static void g_armv7_maccess_operand_print(const GArmV7MAccessOperand *operand, GBufferLine *line)
{
    bool post;                              /* Forme post-indexée ?        */
    bool wback;                             /* Ecriture après coup ?       */

    post = g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7MAOF_POST_INDEXED);
    wback = g_arch_operand_has_flag(G_ARCH_OPERAND(operand), A7MAOF_WRITE_BACK);

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "[", 1, RTT_HOOK, NULL);

    g_arch_operand_print(operand->base, line);

    if (post)
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "]", 1, RTT_HOOK, NULL);

    if (operand->offset != NULL)
    {
        g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
        g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);

        g_arch_operand_print(operand->offset, line);

    }

    if (operand->shift != NULL)
    {
        g_buffer_line_append_text(line, DLC_ASSEMBLY, ",", 1, RTT_PUNCT, NULL);
        g_buffer_line_append_text(line, DLC_ASSEMBLY, " ", 1, RTT_RAW, NULL);

        g_arch_operand_print(operand->shift, line);

    }

    if (!post)
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "]", 1, RTT_HOOK, NULL);

    if (post && wback)
        g_buffer_line_append_text(line, DLC_ASSEMBLY, "!", 1, RTT_PUNCT, NULL);

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

static GArchOperand **g_armv7_maccess_operand_list_inner_instances(const GArmV7MAccessOperand *operand, size_t *count)
{
    GArchOperand **result;                  /* Instances à retourner       */
    size_t idx;                             /* Indice de traitement        */

    *count = 1;

    if (operand->offset != NULL)
        (*count)++;

    if (operand->shift != NULL)
        (*count)++;

    result = malloc(*count * sizeof(GArchOperand *));

    result[0] = operand->base;
    g_object_ref(G_OBJECT(result[0]));

    if (operand->offset != NULL)
    {
        result[1] = operand->offset;
        g_object_ref(G_OBJECT(result[1]));

        idx = 2;

    }
    else
        idx = 1;

    if (operand->shift != NULL)
    {
        result[idx] = operand->shift;
        g_object_ref(G_OBJECT(result[idx]));
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

static void g_armv7_maccess_operand_update_inner_instances(GArmV7MAccessOperand *operand, GArchOperand **instances, size_t count)
{
#ifndef NDEBUG
    size_t idx_check;                       /* Décompte des éléments utiles*/
#endif
    size_t i;                               /* Boucle de parcours          */

#ifndef NDEBUG
    idx_check = 1;

    if (operand->offset != NULL)
        (idx_check)++;

    if (operand->shift != NULL)
        (idx_check)++;

    assert(count == idx_check);
#endif

    for (i = 0; i < count; i++)
    {
        switch (i)
        {
            case 0:
                g_clear_object(&operand->base);
                operand->base = instances[i];
                break;

            case 1:
                if (operand->offset != NULL)
                {
                    g_clear_object(&operand->offset);
                    operand->offset = instances[i];
                }
                else
                {
                    assert(count == 2);

                    g_clear_object(&operand->shift);
                    operand->shift = instances[i];

                }
                break;

            case 2:
                g_clear_object(&operand->shift);
                operand->shift = instances[i];
                break;

        }

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

static guint g_armv7_maccess_operand_hash(const GArmV7MAccessOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    operand_extra_data_t *extra;            /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */
    size_t count;                           /* Quantité d'éléments utiles  */

    extra = GET_ARCH_OP_EXTRA(G_ARCH_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_armv7_maccess_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    count = 1;

    if (operand->offset != NULL)
        (count)++;

    if (operand->shift != NULL)
        (count)++;

    result ^= count;

    if (lock)
        UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}
