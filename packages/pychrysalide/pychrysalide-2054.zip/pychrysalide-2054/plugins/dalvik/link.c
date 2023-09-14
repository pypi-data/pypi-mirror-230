
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.c - édition des liens après la phase de désassemblage
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#include "link.h"


#include <assert.h>
#include <malloc.h>
#include <stdbool.h>
#include <stdio.h>


#include <i18n.h>
#include <analysis/db/items/comment.h>
#include <arch/operands/targetable.h>
#include <common/extstr.h>
#include <plugins/dex/pool.h>


#include "operands/pool.h"
#include "pseudo/switch.h"



/* Mémorisation des cas rencontrés */
typedef struct _case_comment
{
    bool valid;                             /* Entrée utilisable ?         */

    vmpa2t handler;                         /* Position du code associé    */

    bool is_default;                        /* Gestion par défaut ?        */
    union
    {
        int32_t key;                        /* Clef unique                 */
        int32_t *keys;                      /* Ensemble de clefs dynamique */
    };

    size_t count;                           /* Nombre de clefs conservées  */

} case_comment;



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Etablit une référence entre utilisation et origine de chaîne.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_links_for_dalvik_string(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    uint32_t index;                         /* Indice dans la table Dex    */
    GDexPool *pool;                         /* Table de ressources         */
    GBinSymbol *string;                     /* Emplacement de la chaîne    */
    const mrange_t *range;                  /* Zone d'occupation           */
    GArchInstruction *target;               /* Ligne visée par la référence*/

    g_arch_instruction_lock_operands(instr);

    assert(_g_arch_instruction_count_operands(instr) == 2);

    op = _g_arch_instruction_get_operand(instr, 1);

    g_arch_instruction_unlock_operands(instr);

    assert(G_IS_DALVIK_POOL_OPERAND(op));

    assert(g_dalvik_pool_operand_get_pool_type(G_DALVIK_POOL_OPERAND(op)) == DPT_STRING);

    index = g_dalvik_pool_operand_get_index(G_DALVIK_POOL_OPERAND(op));

    pool = g_dex_format_get_pool(G_DEX_FORMAT(format));

    string = g_dex_pool_get_string_symbol(pool, index);

    g_object_unref(G_OBJECT(pool));

    if (string != NULL)
    {
        range = g_binary_symbol_get_range(string);

        target = g_arch_processor_find_instr_by_address(proc, get_mrange_addr(range));

        if (target != NULL)
        {
            g_arch_instruction_link_with(instr, target, ILT_REF);
            g_arch_instruction_link_with(target, instr, ILT_REF);

            g_object_unref(G_OBJECT(target));

        }

        g_object_unref(G_OBJECT(string));

    }

    g_object_unref(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Etablit tous les liens liés à un embranchement compressé.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_dalvik_packed_switch_links(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    const mrange_t *range;                  /* Emplacement de l'instruction*/
    bool defined;                           /* Adresse définie ?           */
    vmpa2t addr;                            /* Adresse de destination      */
    GArchInstruction *switch_ins;           /* Instruction de branchements */
    const vmpa2t *start_addr;               /* Adresse de référentiel      */
    const int32_t *keys;                    /* Conditions de sauts         */
    const int32_t *targets;                 /* Positions relatives liées   */
    uint16_t count;                         /* Taille de ces tableaux      */
    case_comment *comments;                 /* Mémorisation progressive    */
    vmpa2t def_addr;                        /* Traitement par défaut       */
    GArchInstruction *target;               /* Ligne visée par la référence*/
    case_comment *comment;                  /* Commentaire à éditer        */
    uint16_t i;                             /* Boucle de parcours #1       */
    uint16_t j;                             /* Boucle de parcours #2       */
    int32_t tmp;                            /* Sauvegarde temporaire       */
    char *msg;                              /* Indication à imprimer       */
    size_t k;                               /* Boucle de parcours #3       */
    char *int_val;                          /* Valeur en chaîne de carac.  */
    GDbComment *item;                       /* Indication sur la condition */

    g_arch_instruction_lock_operands(instr);

    assert(_g_arch_instruction_count_operands(instr) == 2);

    op = _g_arch_instruction_get_operand(instr, 1);

    g_arch_instruction_unlock_operands(instr);

    if (G_IS_TARGETABLE_OPERAND(op))
    {
        range = g_arch_instruction_get_range(instr);

        defined = g_targetable_operand_get_addr(G_TARGETABLE_OPERAND(op), get_mrange_addr(range),
                                                G_BIN_FORMAT(format), proc, &addr);
    }

    else
        defined = false;

    g_object_unref(G_OBJECT(op));

    if (defined)
    {
        switch_ins = g_arch_processor_find_instr_by_address(proc, &addr);

        if (G_IS_DALVIK_SWITCH_INSTR(switch_ins))
        {
            range = g_arch_instruction_get_range(instr);

            start_addr = get_mrange_addr(range);

            /* Préparation de l'édition des commentaires */

            count = g_dalvik_switch_get_data(G_DALVIK_SWITCH_INSTR(switch_ins), &keys, &targets);

            comments = (case_comment *)calloc(1 + count, sizeof(case_comment));

            /* Cas par défaut */

            compute_mrange_end_addr(range, &def_addr);

            target = g_arch_processor_find_instr_by_address(proc, &def_addr);

            if (target != NULL)
            {
                comment = &comments[0];

                comment->valid = true;

                copy_vmpa(&comment->handler, &def_addr);

                comment->is_default = true;

                g_arch_instruction_link_with(instr, target, ILT_CASE_JUMP);

                g_object_unref(G_OBJECT(target));

            }

            /* Autres cas */

            for (i = 0; i < count; i++)
            {
                copy_vmpa(&addr, start_addr);
                advance_vmpa(&addr, targets[i] * sizeof(uint16_t));

                if (cmp_vmpa(&addr, &def_addr) == 0)
                    continue;

                target = g_arch_processor_find_instr_by_address(proc, &addr);

                if (target != NULL)
                {
                    for (j = 0; j < (1 + count); j++)
                    {
                        if (!comments[j].valid)
                            break;

                        if (cmp_vmpa(&addr, &comments[j].handler) == 0)
                            break;

                    }

                    assert(j < (1 + count));

                    comment = &comments[j];

                    if (!comment->valid)
                    {
                        comment->valid = true;

                        copy_vmpa(&comment->handler, &addr);

                        comment->key = keys[i];
                        comment->count = 1;

                    }
                    else
                    {
                        if (comment->count == 0)
                            comment->key = keys[i];

                        if (comment->count == 1)
                        {
                            tmp = comment->key;

                            comment->keys = (int32_t *)calloc(2, sizeof(int32_t));

                            comment->keys[0] = tmp;
                            comment->keys[1] = keys[i];

                            comment->count = 2;

                        }

                        else
                        {
                            comment->count++;

                            comment->keys = (int32_t *)realloc(comment->keys, comment->count * sizeof(int32_t));

                            comment->keys[comment->count - 1] = keys[i];

                        }

                    }

                    g_arch_instruction_link_with(instr, target, ILT_CASE_JUMP);

                    g_object_unref(G_OBJECT(target));

                }

            }

            /* Edition des commentaires et nettoyage */

            for (j = 0; j < (1 + count); j++)
            {
                comment = &comments[j];

                if (!comment->valid)
                    break;

                switch (comment->count)
                {
                    case 0:
                        msg = NULL;
                        break;

                    case 1:
                        asprintf(&msg, _("Case %d"), comment->key);
                        break;

                    default:

                        msg = NULL;

                        /**
                         * Les spécifications indiquent que les clefs sont triées.
                         * Donc nul besoin de s'occuper de leur ordre ici.
                         */

                        for (k = 0; k < comment->count; k++)
                        {
                            if (k > 0)
                                msg = stradd(msg, "\n");

                            asprintf(&int_val, _("Case %d:"), comment->keys[k]);
                            msg = stradd(msg, int_val);
                            free(int_val);

                        }

                        break;

                }

                if (comment->is_default)
                {
                    if (msg == NULL)
                        msg = strdup(_("Defaut case:"));
                    else
                    {
                        msg = stradd(msg, "\n");
                        msg = stradd(msg, _("Defaut case"));
                    }

                }

                item = g_db_comment_new(&comment->handler, CET_BEFORE, BLF_NONE, msg);

                g_db_item_add_flag(G_DB_ITEM(item), DIF_VOLATILE);
                g_proc_context_add_db_item(context, G_DB_ITEM(item));

                free(msg);

                if (comment->count > 1)
                    free(comment->keys);

            }

            free(comments);

        }

        if (switch_ins != NULL)
            g_object_unref(G_OBJECT(switch_ins));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Etablit une référence entre appelant et appelé.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_links_between_caller_and_callee(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    uint32_t index;                         /* Indice dans la table Dex    */
    GDexPool *pool;                         /* Table de ressources         */
    GDexMethod *method;                     /* Méthode ciblée ici          */
    GBinRoutine *routine;                   /* Routine liée à la méthode   */
    const mrange_t *range;                  /* Zone d'occupation           */
    GArchInstruction *target;               /* Ligne visée par la référence*/

    g_arch_instruction_lock_operands(instr);

    assert(_g_arch_instruction_count_operands(instr) == 2);

    op = _g_arch_instruction_get_operand(instr, 1);

    g_arch_instruction_unlock_operands(instr);

    assert(G_IS_DALVIK_POOL_OPERAND(op));

    assert(g_dalvik_pool_operand_get_pool_type(G_DALVIK_POOL_OPERAND(op)) == DPT_METHOD);

    index = g_dalvik_pool_operand_get_index(G_DALVIK_POOL_OPERAND(op));

    pool = g_dex_format_get_pool(G_DEX_FORMAT(format));

    method = g_dex_pool_get_method(pool, index);

    g_object_unref(G_OBJECT(pool));

    if (method != NULL)
    {
        routine = g_dex_method_get_routine(method);
        range = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

        if (range->addr.physical > 0)
        {
            target = g_arch_processor_find_instr_by_address(proc, get_mrange_addr(range));

            if (target != NULL)
            {
                g_arch_instruction_link_with(instr, target, ILT_REF);

                g_object_unref(G_OBJECT(target));

            }

        }

        g_object_unref(G_OBJECT(routine));
        g_object_unref(G_OBJECT(method));

    }

    g_object_unref(G_OBJECT(op));

}
