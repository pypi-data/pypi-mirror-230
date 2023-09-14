
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collect.c - collecte de différents registres en remontant le flot d'exécution
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "collect.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <arch/operands/register.h>


#include "hops.h"



/* Suivi de l'usage d'un registre */
typedef struct _collected_register
{
    GArchRegister *reg;                     /* Registre usité à tracer     */

    bool required;                          /* Registre utile ?            */

    GArchInstruction *written;              /* Emplacement d'écriture      */

} collected_register;

/* Suivi d'un flot d'exécution */
typedef struct _call_stack
{
    collected_register *registers;          /* Liste de registres suivis   */
    size_t count;                           /* Taille de cette liste       */

    instr_iter_t *iter;                     /* Boucle de parcours          */
    bool use_current;                       /* Traite l'instruction pointée*/

    bool skip_syscall;                      /* Acceptation des rencontres  */

} call_stack;

/* Collection de registres */
struct _tracked_path
{
    call_stack *stacks;                     /* Piles d'exécution suivies   */
    size_t count;                           /* Nombre de ces piles         */

};


/* Copie les informations de pile d'appels. */
static void copy_call_stack(call_stack *, const call_stack *);

/* Libère la mémoire des infos relatives à une pile d'appels. */
static void clean_call_stack(call_stack *);

/* Fournit une structure de suivi de registres pour une branche. */
static size_t fork_register_tracker(tracked_path *, size_t, GArchProcessor *, GArchInstruction *);

/* Change la tête de lecture pour le parcours des instructions. */
static void change_register_tracker_iter(tracked_path *, size_t, GArchProcessor *, GArchInstruction *);

/* Détermine si tous les registres recherchés ont été trouvés. */
static bool got_all_tracked_registers(const tracked_path *, size_t);



/******************************************************************************
*                                                                             *
*  Paramètres  : dest = zone de destination des données copiées. [OUT]        *
*                src  = source des données à copier.                          *
*                                                                             *
*  Description : Copie les informations de pile d'appels.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void copy_call_stack(call_stack *dest, const call_stack *src)
{
    size_t i;                               /* Boucle de parcours          */

    if (src->count == 0)
    {
        dest->registers = NULL;
        dest->count = 0;
    }

    else
    {
        dest->registers = (collected_register *)malloc(src->count * sizeof(collected_register));
        dest->count = src->count;

        for (i = 0; i < src->count; i++)
        {
            dest->registers[i].reg = src->registers[i].reg;
            dest->registers[i].required = src->registers[i].required;
            dest->registers[i].written = src->registers[i].written;

            g_object_ref(G_OBJECT(dest->registers[i].reg));

            if (dest->registers[i].written != NULL)
                g_object_ref(G_OBJECT(dest->registers[i].written));

        }

    }

    dest->iter = src->iter != NULL ? copy_instruction_iterator(src->iter) : NULL;
    dest->use_current = src->use_current;

    dest->skip_syscall = src->skip_syscall;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = information sur une pile d'appels à supprimer.       *
*                                                                             *
*  Description : Libère la mémoire des infos relatives à une pile d'appels.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void clean_call_stack(call_stack *stack)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < stack->count; i++)
    {
        g_object_unref(G_OBJECT(stack->registers[i].reg));

        if (stack->registers[i].written != NULL)
            g_object_unref(G_OBJECT(stack->registers[i].written));

    }

    if (stack->registers != NULL)
        free(stack->registers);

    if (stack->iter != NULL)
        delete_instruction_iterator(stack->iter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base = position de parcours initiale.                        *
*                                                                             *
*  Description : Crée une structure de suivi de registres vide.               *
*                                                                             *
*  Retour      : Structure prête à emploi.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

tracked_path *create_register_tracker(instr_iter_t *base)
{
    tracked_path *result;                   /* Structure à retourner       */

    result = (tracked_path *)malloc(sizeof(tracked_path));

    result->stacks = (call_stack *)malloc(sizeof(call_stack));
    result->count = 1;

    copy_call_stack(&result->stacks[0],
                    (call_stack []) {
                        {
                            .count = 0,
                            .iter = base,
                            .use_current = true,
                            .skip_syscall = true
                        }
                    });

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model = suivi déjà en place d'où l'inspiration doit venir.   *
*                sid   = identifiant de la pile d'exécution initiale.         *
*                                                                             *
*  Description : Crée une structure de suivi de registres initialisée.        *
*                                                                             *
*  Retour      : Structure prête à emploi.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

tracked_path *create_register_tracker_from(const tracked_path *model, size_t sid)
{
    tracked_path *result;                   /* Structure à retourner       */

    result = (tracked_path *)malloc(sizeof(tracked_path));

    result->stacks = (call_stack *)malloc(sizeof(call_stack));
    result->count = 1;

    copy_call_stack(&result->stacks[0], &model->stacks[sid]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à traiter.                         *
*                                                                             *
*  Description : Efface une structure de suivi de registres.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_register_tracker(tracked_path *path)
{
    size_t i;                               /* Boucle de parcours          */

    assert(path->count >= 1);

    for (i = 0; i < path->count; i++)
        clean_call_stack(&path->stacks[i]);

    free(path->stacks);

    free(path);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à consulter.                       *
*                                                                             *
*  Description : Dénombre les piles d'exécutions différentes conservées.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t count_register_tracker_stacks(const tracked_path *path)
{
    size_t result;                          /* Quantité à retourner        */

    result = path->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à traiter.                         *
*                sid  = identifiant de la pile d'exécution racine à copier.   *
*                proc = processeur de l'architecture pour les instructions.   *
*                dest = prochaine instruction à traiter.                      *
*                                                                             *
*  Description : Fournit une structure de suivi de registres pour une branche.*
*                                                                             *
*  Retour      : Indice de la nouvelle pile d'exécution à suivre.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t fork_register_tracker(tracked_path *path, size_t sid, GArchProcessor *proc, GArchInstruction *dest)
{
    size_t result;                          /* Indice à retourner          */

    result = path->count;

    path->stacks = (call_stack *)realloc(path->stacks, ++path->count * sizeof(call_stack));

    copy_call_stack(&path->stacks[result], &path->stacks[sid]);

    change_register_tracker_iter(path, result, proc, dest);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à traiter.                         *
*                sid  = identifiant de la pile d'exécution à traiter.         *
*                proc = processeur de l'architecture pour les instructions.   *
*                dest = prochaine instruction à traiter.                      *
*                                                                             *
*  Description : Change la tête de lecture pour le parcours des instructions. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_register_tracker_iter(tracked_path *path, size_t sid, GArchProcessor *proc, GArchInstruction *dest)
{
    const mrange_t *range;                  /* Couverture d'une instruction*/
    instr_iter_t *iter;                     /* Tête de lecture             */

    if (path->stacks[sid].iter != NULL)
        delete_instruction_iterator(path->stacks[sid].iter);

    range = g_arch_instruction_get_range(dest);
    iter = g_arch_processor_get_iter_from_address(proc, get_mrange_addr(range));

    path->stacks[sid].iter = iter;
    path->stacks[sid].use_current = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path  = chemin d'exécution à traiter.                        *
*                sid   = identifiant de la pile d'exécution à traiter.        *
*                reg   = registre concerné par la procédure.                  *
*                where = localisation de l'écriture ou importance de la note. *
*                                                                             *
*  Description : Note le besoin ou l'usage d'un registre donné.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void mark_register_in_tracker(tracked_path *path, size_t sid, GArchRegister *reg, GArchInstruction *where)
{
    call_stack *stack;                      /* Pile d'exécution concernée  */
    size_t i;                               /* Boucle de parcours          */
    collected_register *collected;          /* Accès simplifié             */
    int ret;                                /* Bilan d'une comparaison     */

    stack = &path->stacks[sid];

    /* Mise à jour d'un élément présent ? */

    for (i = 0; i < stack->count; i++)
    {
        collected = &stack->registers[i];

        ret = g_arch_register_compare(collected->reg, reg);
        if (ret != 0) continue;

        if (where == NULL)
            collected->required = true;

        else
        {
            if (collected->written == NULL)
            {
                collected->written = where;
                g_object_ref(G_OBJECT(where));
            }

        }

        break;

    }

    /* Ajout d'une nouvelle note */

    if (i == stack->count)
    {
        stack->count++;
        stack->registers = (collected_register *)realloc(stack->registers,
                                                         stack->count * sizeof(collected_register));

        collected = &stack->registers[stack->count - 1];

        collected->reg = reg;
        g_object_ref(G_OBJECT(reg));

        if (where == NULL)
        {
            collected->required = true;
            collected->written = NULL;
        }

        else
        {
            collected->required = false;
            collected->written = where;
            g_object_ref(G_OBJECT(where));
        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à consulter.                       *
*                sid   = identifiant de la pile d'exécution à traiter.        *
*                                                                             *
*  Description : Détermine si tous les registres recherchés ont été trouvés.  *
*                                                                             *
*  Retour      : Besoin en poursuite d'études.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool got_all_tracked_registers(const tracked_path *path, size_t sid)
{
    bool result;                            /* Bilan à retourner           */
    call_stack *stack;                      /* Pile d'exécution concernée  */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    stack = &path->stacks[sid];

    for (i = 0; i < stack->count && result; i++)
        if (stack->registers[i].required)
            result = (stack->registers[i].written != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à consulter et compléter.          *
*                sid  = identifiant de la pile d'exécution à traiter.         *
*                proc = processeur de l'architecture pour les instructions.   *
*                hops = opérations spécialement adaptées à une architecture.  *
*                                                                             *
*  Description : Se lance à la recherche de la définition de registres.       *
*                                                                             *
*  Retour      : true si toutes les définitions demandées ont été trouvées.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool look_for_registers(tracked_path *path, size_t sid, GArchProcessor *proc, const hunting_ops *hops)
{
    bool result;                            /* Bilan de l'opération        */
    call_stack *stack;                      /* Pile d'exécution concernée  */
    GArchInstruction *instr;                /* Instruction analysée        */
    GArchOperand *operand;                  /* Destination d'instruction ? */
    GArchRegister *reg;                     /* Registre en première ligne  */
    size_t count;                           /* Nombre de sources présentes */
    bool first;                             /* Premier aiguillage ?        */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *link;               /* Détails d'un lien           */
    size_t next;                            /* Indice de la pile suivante  */

    stack = &path->stacks[sid];

    while (stack->iter != NULL && !got_all_tracked_registers(path, sid))
    {
        if (stack->use_current)
        {
            instr = get_instruction_iterator_current(stack->iter);
            stack->use_current = false;
        }

        else
            instr = get_instruction_iterator_prev(stack->iter);

        /* Détection de fin de parcours (#1) */

        if (instr == NULL)
        {
            delete_instruction_iterator(stack->iter);
            stack->iter = NULL;
            break;
        }

        if (hops->is_syscall(instr) && !stack->skip_syscall)
        {
            delete_instruction_iterator(stack->iter);
            stack->iter = NULL;
            break;
        }

        stack->skip_syscall = false;

        /* Traitement de l'instruction courante */

        g_arch_instruction_lock_operands(instr);

        if (_g_arch_instruction_count_operands(instr) > 0)
        {
            operand = _g_arch_instruction_get_operand(instr, 0);

            if (G_IS_REGISTER_OPERAND(operand))
            {
                reg = g_register_operand_get_register(G_REGISTER_OPERAND(operand));

                mark_register_in_tracker(path, sid, reg, instr);

            }

            g_object_unref(G_OBJECT(operand));

        }

        g_arch_instruction_unlock_operands(instr);

        /* Détermination de l'instruction suivante */

        g_arch_instruction_lock_src(instr);

        count = g_arch_instruction_count_sources(instr);

        first = true;

        for (i = 0; i < count; i++)
        {
            link = g_arch_instruction_get_source(instr, i);

            switch (link->type)
            {
                case ILT_EXEC_FLOW:
                case ILT_JUMP:
                case ILT_CASE_JUMP:
                case ILT_JUMP_IF_TRUE:
                case ILT_JUMP_IF_FALSE:

                    if (first)
                    {
                        change_register_tracker_iter(path, sid, proc, link->linked);
                        first = false;
                    }

                    else
                    {
                        next = fork_register_tracker(path, sid, proc, link->linked);
                        look_for_registers(path, next, proc, hops);

                        /**
                         * Rechargement car un fork_register_tracker() a pu déplacer la liste via realloc().
                         */
                        stack = &path->stacks[sid];

                    }

                    break;

                default:
                    break;

            }

            unref_instr_link(link);

        }

        g_arch_instruction_unlock_src(instr);

        /* Détection de fin de parcours (#2) */

        if (g_arch_instruction_get_flags(instr) & AIF_ROUTINE_START)
        {
            delete_instruction_iterator(stack->iter);
            stack->iter = NULL;
            break;
        }

    }

    result = got_all_tracked_registers(path, sid);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'exécution à traiter.                         *
*                sid   = identifiant de la pile d'exécution à traiter.        *
*                reg  = registre concerné par la procédure.                   *
*                                                                             *
*  Description : Retrouve la dernière modification d'un registre donné.       *
*                                                                             *
*  Retour      : Localisation de l'écriture ou importante de la note.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *get_register_write_location(const tracked_path *path, size_t sid, const GArchRegister *reg)
{
    GArchInstruction *result;               /* Emplacement à retourner     */
    call_stack *stack;                      /* Pile d'exécution concernée  */
    size_t i;                               /* Boucle de parcours          */
    collected_register *collected;          /* Accès simplifié             */
    int ret;                                /* Bilan d'une comparaison     */

    result = NULL;

    stack = &path->stacks[sid];

    for (i = 0; i < stack->count; i++)
    {
        collected = &stack->registers[i];

        ret = g_arch_register_compare(collected->reg, reg);
        if (ret != 0) continue;

        result = collected->written;

        if (result != NULL)
            g_object_ref(G_OBJECT(result));

        break;

    }

    return result;

}
