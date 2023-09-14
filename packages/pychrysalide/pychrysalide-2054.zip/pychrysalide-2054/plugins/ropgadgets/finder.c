
/* Chrysalide - Outil d'analyse de fichiers binaires
 * finder.c - recherche de gadgets pour ROP
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "finder.h"


#include <malloc.h>
#include <string.h>


#include <core/processors.h>
#include <format/known.h>


#include "helper.h"
#include "helper_arm.h"



/* Actions selon l'architecture */
typedef struct _domain_ops
{
    size_t (* list) (char ***);
    GProcContext * (* get) (const GArchProcessor *, size_t);

    const phys_t * (* setup) (size_t *);

} domain_ops;

/* Données utiles à transmettre */
typedef struct _search_domain
{
    GExeFormat *format;                     /* Format du fichier binaire   */
    GBinContent *content;                   /* Contenu associé récupéré    */
    GArchProcessor *proc;                   /* Processeur idéal en place   */

    domain_ops ops;                         /* Actions particulières       */

    mrange_t *exe_ranges;                   /* Liste de zones exécutables  */
    size_t exe_count;                       /* Nombre de ces zones         */

    phys_t sum;                             /* Surface totale à parcourir  */
    size_t runs_count;                      /* Nombre de passages à faire  */
    size_t runs_done;                       /* Nombre de passages effectués*/

} search_domain;


/* Désassemble rapidement une instruction. */
static GArchInstruction *disassemble_instruction_in_domain(const search_domain *, size_t, vmpa2t *);

/* Etend la constitution d'une chaîne d'instructions. */
static rop_chain *push_new_instruction(rop_chain *, GArchInstruction *);

/* Désassemble en amont d'une position autant que possible. */
static void look_backward_for_gadgets(const search_domain *, size_t, const mrange_t *, const vmpa2t *, unsigned int, rop_chain *);

/* Etablit une liste de tous les gadgets présents. */
static rop_chain **list_all_gadgets_in_domain(const search_domain *, size_t, unsigned int, update_search_progress_cb, GObject *, size_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : domain = ensemble d'auxiliaires à disposition.               *
*                index = indice du type de contexte désiré.                   *
*                pos    = tête de lecture pour le désassemblage.              *
*                                                                             *
*  Description : Désassemble rapidement une instruction.                      *
*                                                                             *
*  Retour      : Instruction créée ou NULL en cas d'échec.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *disassemble_instruction_in_domain(const search_domain *domain, size_t index, vmpa2t *pos)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    GProcContext *ctx;                      /* Contexte de désassemblage   */

    ctx = domain->ops.get(domain->proc, index);

    result = g_arch_processor_disassemble(domain->proc, ctx, domain->content, pos, domain->format);

    if (result != NULL)
    {
        g_arch_instruction_call_hook(result, IPH_LINK, domain->proc, ctx, domain->format);
        g_arch_instruction_call_hook(result, IPH_POST, domain->proc, ctx, domain->format);
    }

    g_object_unref(G_OBJECT(ctx));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instrs = liste d'instructions à compléter ou NULL.           *
*                instr  = nouvelle instruction à ajouter.                     *
*                                                                             *
*  Description : Etend la constitution d'une chaîne d'instructions.           *
*                                                                             *
*  Retour      : Série d'instruction complétée.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static rop_chain *push_new_instruction(rop_chain *chain, GArchInstruction *instr)
{
    rop_chain *result;                      /* Chaîne à retourner          */

    if (chain == NULL)
    {
        result = (rop_chain *)calloc(1, sizeof(rop_chain));

        result->instrs = (GArchInstruction **)calloc(1, sizeof(GArchInstruction *));
        result->count = 1;

    }
    else
    {
        result = chain;

        result->count++;
        result->instrs = (GArchInstruction **)realloc(result->instrs, result->count * sizeof(GArchInstruction *));

    }

    if (result->count > 1)
        memmove(&result->instrs[1], &result->instrs[0], (result->count - 1) * sizeof(GArchInstruction *));

    result->instrs[0] = instr;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : domain    = ensemble d'auxiliaires à disposition.            *
*                index     = indice du type de contexte désiré.               *
*                exe_range = couverture globale dont il ne faut pas sortir.   *
*                ret       = point de retour final déjà trouvé.               *
*                max_depth = profondeur maximale des recherches.              *
*                chain     = chaîne d'instructions à compléter. [OUT]         *
*                                                                             *
*  Description : Désassemble en amont d'une position autant que possible.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void look_backward_for_gadgets(const search_domain *domain, size_t index, const mrange_t *exe_range, const vmpa2t *ret, unsigned int max_depth, rop_chain *chain)
{
    const phys_t *ins_sizes;                /* Tailles potentielles        */
    size_t sizes_count;                     /* Quantité de tailles à tester*/
    vmpa2t last;                            /* Dernier point de départ     */
    unsigned int i;                         /* Boucle de parcours #1       */
    GArchInstruction *instr;                /* Elément de gadget trouvé    */
    size_t k;                               /* Boucle de parcours #2       */
    vmpa2t start;                           /* Point de départ courant     */
    vmpa2t end;                             /* Point d'arrivée obtenu      */
    phys_t diff;                            /* Volume de données traité    */
    mrange_t range;                         /* Couverture de l'instruction */

    ins_sizes = domain->ops.setup(&sizes_count);

    copy_vmpa(&last, ret);

    /* On parcours jusqu'à la profondeur maximale */
    for (i = 0; i < max_depth; i++)
    {
        instr = NULL;

        for (k = 0; k < sizes_count && instr == NULL; k++)
        {
            copy_vmpa(&start, &last);
            deminish_vmpa(&start, ins_sizes[k]);

            /* Est-on toujours dans les clous ? */
            if (!mrange_contains_addr(exe_range, &start)) break;

            copy_vmpa(&end, &start);

            instr = disassemble_instruction_in_domain(domain, index, &end);
            if (instr == NULL) continue;

            /* La jointure est-elle parfaite ? */

            if (cmp_vmpa(&end, &last) != 0)
            {
                g_object_unref(G_OBJECT(instr));
                instr = NULL;
                continue;
            }

            /* S'il s'agit d'un point de retour, on laisse la main à une autre liste */

            if (g_arch_instruction_get_flags(instr) & AIF_RETURN_POINT)
            {
                g_object_unref(G_OBJECT(instr));
                instr = NULL;
                continue;
            }

        }

        /* Aucune instruction n'a été trouvée à cette profondeur, on s'arrête donc */
        if (instr == NULL) break;

        copy_vmpa(&last, &start);

        diff = compute_vmpa_diff(&end, &start);

        init_mrange(&range, &start, diff);

        g_arch_instruction_set_range(instr, &range);

        push_new_instruction(chain, instr);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : domain    = ensemble d'auxiliaires à disposition.            *
*                index     = indice du type de contexte désiré.               *
*                max_depth = profondeur maximale des recherches.              *
*                update    = fonction de suivi mise à disposition.            *
*                data      = données à associer à une phase d'actualisation.  *
*                count     = nombre de gadgets trouvés. [OUT]                 *
*                                                                             *
*  Description : Etablit une liste de tous les gadgets présents.              *
*                                                                             *
*  Retour      : Liste de listes d'instructions, à libérer après usage.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static rop_chain **list_all_gadgets_in_domain(const search_domain *domain, size_t index, unsigned int max_depth, update_search_progress_cb update, GObject *data, size_t *count)
{
    rop_chain **result;                     /* Liste de listes à renvoyer  */
    phys_t done;                            /* Accumulation des quantités  */
    size_t i;                               /* Boucle de parcours #1       */
    phys_t max;                             /* Borne d'un parcours         */
    phys_t k;                               /* Boucle de parcours #2       */
    gdouble fraction;                       /* Progression générale        */
    vmpa2t ret;                             /* Emplacement du retour       */
    vmpa2t tmp;                             /* Copie de travail modifiable */
    GArchInstruction *gadget;               /* Nouveau gadget détecté      */
    phys_t diff;                            /* Volume de données traité    */
    mrange_t ins_range;                     /* Emplacement d'une instruct° */
    vmpa2t end;                             /* Point d'arrivée obtenu      */
    rop_chain *chain;                       /* Nouvelle chaîne trouvée     */

    result = NULL;
    *count = 0;

    done = 0;

    for (i = 0; i < domain->exe_count; i++)
    {
        max = get_mrange_length(&domain->exe_ranges[i]);

        for (k = 0; k < max; k++)
        {
            /* Affichage de la progression */

            fraction = 1.0 * (domain->runs_done * domain->sum + done + k);
            fraction /= (domain->runs_count * domain->sum);

            update(data, fraction);

            /* Réception de la première / dernière instruction */

            copy_vmpa(&ret, get_mrange_addr(&domain->exe_ranges[i]));
            advance_vmpa(&ret, k);

            copy_vmpa(&tmp, &ret);

            gadget = disassemble_instruction_in_domain(domain, index, &tmp);
            if (gadget == NULL) continue;

            /* A-t-on bien affaire à une instruction de retour ? */

            if (!(g_arch_instruction_get_flags(gadget) & AIF_RETURN_POINT))
            {
                g_object_unref(G_OBJECT(gadget));
                continue;
            }

            /* Ne déborde-t-on pas dans une zone voisine ? */

            diff = compute_vmpa_diff(&ret, &tmp);
            init_mrange(&ins_range, &ret, diff);

            compute_mrange_end_addr(&ins_range, &end);

            if (!mrange_contains_mrange(&domain->exe_ranges[i], &ins_range))
            {
                g_object_unref(G_OBJECT(gadget));
                continue;
            }

            /* Ajout d'un nouvel ensemble de gadgets */

            g_arch_instruction_set_range(gadget, &ins_range);

            chain = push_new_instruction(NULL, gadget);

            look_backward_for_gadgets(domain, index, &domain->exe_ranges[i], &ret, max_depth, chain);

            result = (rop_chain **)realloc(result, ++(*count) * sizeof(rop_chain *));
            result[*count - 1] = chain;

        }

        done += max;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary    = binaire dont le contenu est à traiter.           *
*                max_depth = profondeur maximale des recherches.              *
*                update    = fonction de suivi mise à disposition.            *
*                data      = données à associer à une phase d'actualisation.  *
*                count     = nombre de gadgets trouvés. [OUT]                 *
*                                                                             *
*  Description : Etablit une liste de tous les gadgets présents.              *
*                                                                             *
*  Retour      : Liste de listes d'instructions, à libérer après usage.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

found_rop_list *list_all_gadgets(GExeFormat *format, unsigned int max_depth, update_search_progress_cb update, GObject *data, size_t *count)
{
    found_rop_list *result;                 /* Liste de listes à renvoyer  */
    const char *target;                     /* Sous-traitance requise      */
    search_domain domain;                   /* Outils pour la recherche    */
    GBinPortion *portions;                  /* Couche première de portions */
    char **names;                           /* Désignations humaines liées */
    size_t i;                               /* Boucle de parcours          */

    /* Constitution du socle commun */

    g_object_ref(G_OBJECT(format));
    domain.format = format;

    domain.content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    target = g_exe_format_get_target_machine(format);
    domain.proc = get_arch_processor_for_key(target);

    bool collect_x_ranges(GBinPortion *portion, GBinPortion *parent, BinaryPortionVisit visit, void *unused)
    {
        const mrange_t *range;

        if (visit == BPV_SHOW)
        {
            if (g_binary_portion_get_rights(portion) & PAC_EXEC)
            {
                range = g_binary_portion_get_range(portion);

                domain.exe_ranges = (mrange_t *)realloc(domain.exe_ranges, ++domain.exe_count * sizeof(mrange_t));
                copy_mrange(&domain.exe_ranges[domain.exe_count - 1], range);

            }

        }

        return true;

    }

    domain.exe_ranges = NULL;
    domain.exe_count = 0;

    portions = g_exe_format_get_portions(format);

    g_binary_portion_visit(portions, (visit_portion_fc)collect_x_ranges, NULL);

    g_object_unref(G_OBJECT(portions));

    /* Récupération des différents contextes */

    if (strcmp(target, "armv7") == 0)
    {
        domain.ops.list = list_rop_contexts_for_arm;
        domain.ops.get = get_rop_contexts_for_arm;
        domain.ops.setup = setup_instruction_sizes_for_arm;
    }
    else
    {
        domain.ops.list = list_rop_contexts_by_default;
        domain.ops.get = get_rop_contexts_by_default;
        domain.ops.setup = setup_instruction_sizes_by_default;
    }

    *count = domain.ops.list(&names);

    /* Calcul de la surface totale à parcourir */

    domain.sum = 0;

    for (i = 0; i < domain.exe_count; i++)
        domain.sum += get_mrange_length(&domain.exe_ranges[i]);

    /* Détermination des différents parcours */

    domain.runs_count = *count;

    domain.runs_done = 0;

    /* Parcours des différentes surfaces */

    result = (found_rop_list *)calloc(*count, sizeof(found_rop_list));

    for (i = 0; i < *count; i++)
    {
        result[i].category = names[i];

        result[i].gadgets = list_all_gadgets_in_domain(&domain, i, max_depth, update, data, &result[i].count);

        domain.runs_done++;

    }

    free(names);

    free(domain.exe_ranges);

    g_object_unref(G_OBJECT(domain.proc));
    g_object_unref(G_OBJECT(domain.content));
    g_object_unref(G_OBJECT(domain.format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de gadgets trouvés à supprimer.              *
*                                                                             *
*  Description : Libère la mémoire des gadgets trouvés pour du ROP.           *
*                                                                             *
*  Retour      :                                                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void free_rop_list(found_rop_list *list)
{
    size_t i;                               /* Boucle de parcours #1       */
    rop_chain *chain;                       /* Accès direct à une chaîne   */
    size_t j;                               /* Boucle de parcours #2       */

    for (i = 0; i < list->count; i++)
    {
        chain = list->gadgets[i];

        for (j = 0; j < chain->count; j++)
            g_object_unref(G_OBJECT(chain->instrs[j]));

        free(chain->instrs);
        free(chain);

    }

    free(list->gadgets);
    free(list);

}
