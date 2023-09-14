
/* Chrysalide - Outil d'analyse de fichiers binaires
 * try_n_catch.c - support des exceptions chez Android
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#include "try_n_catch.h"


#include <malloc.h>
#include <stdio.h>


#include <format/dex/dex-int.h>
#include <format/dex/pool.h>
#include <gtkext/gtkblockdisplay.h>
#include <../i18n.h>



/* Mémorisation d'un lien vers un gestionnaire */
typedef struct _caught_exception
{
    vmpa_t addr;                            /* Adresse du code de gestion  */
    GArchInstruction *instr;                /* Première instruction visée  */
    char *desc;                             /* Nom de l'exception          */

} caught_exception;



/* Valide la zone couverte par le gestionnaire d'exceptions. */
static bool check_covered_area(const try_item *, const GBinRoutine *);

/* Rattache les gestionnaires d'exception à leur code couvert. */
static void attach_caught_code(const GLoadedBinary *, const GBinRoutine *, const try_item *, const caught_exception *, size_t);

/* Insère des indications dans le texte humainement lisibles. */
static void mark_exception_handlers(const GLoadedBinary *, uleb128_t, caught_exception **, size_t *);

/* Construit des listes pointant sur les différentes gestions. */
static caught_exception **build_all_destinations_list(const GLoadedBinary *, const GBinRoutine *, const encoded_catch_handler_list *, size_t **);

/* Recherche et met en avant tous les gestionnaires d'exception. */
static void look_for_exception_handlers(const GLoadedBinary *, const GDexFormat *, GDexMethod *, bool);



/******************************************************************************
*                                                                             *
*  Paramètres  : try     = informations sur la gestion à consulter.           *
*                routine = routine associée, pour validation.                 *
*                                                                             *
*  Description : Valide la zone couverte par le gestionnaire d'exceptions.    *
*                                                                             *
*  Retour      : Validité de la zone couverte.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool check_covered_area(const try_item *try, const GBinRoutine *routine)
{
    off_t length;                           /* Taille de la zone de code   */
    vmpa_t covered_start;                   /* Début de la zone couverte   */
    vmpa_t covered_end;                     /* Fin de la zone couverte     */
    const mrange_t *range;                  /* Emplacement du symbole      */

    covered_start = try->start_addr * sizeof(uint16_t);
    covered_end = covered_start + try->insn_count * sizeof(uint16_t);

    range = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

    return (covered_end <= get_mrange_length(range));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary   = représentation binaire à traiter.                 *
*                routine  = routine associée, pour l'accès au instructions.   *
*                try      = informations sur la gestion à consulter.          *
*                handlers = arrivées des liens vers les gestionnaires.        *
*                count    = nombre de ces arrivées.                           *
*                                                                             *
*  Description : Rattache les gestionnaires d'exception à leur code couvert.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void attach_caught_code(const GLoadedBinary *binary, const GBinRoutine *routine, const try_item *try, const caught_exception *handlers, size_t count)
{
    const mrange_t *range;                  /* Emplacement du symbole      */
    vmpa_t start;                           /* Début de la zone couverte   */
    vmpa_t end;                             /* Fin de la zone couverte     */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GArchInstruction *instrs;               /* Instructions Dalvik         */
    GArchInstruction *first;                /* Première instruction        */
    GArchInstruction *next;                 /* Dernière instruction + 1    */
    GArchInstruction *prev;                 /* Instruction à détacher      */
    GArchInstruction *iter;                 /* Boucle de parcours #1       */
    size_t i;                               /* Boucle de parcours #2       */

    range = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

    start = get_mrange_addr(range)->virtual;
    start += try->start_addr * sizeof(uint16_t);

    end = start + try->insn_count * sizeof(uint16_t);

    proc = g_loaded_binary_get_processor(binary);
    instrs = NULL;//g_arch_processor_get_disassembled_instructions(proc);

    first = g_arch_instruction_find_by_address(instrs, start, true);
    next = g_arch_instruction_find_by_address(instrs, end, true);

    if (first == NULL || next == NULL)
        goto acc_exit;

    /* Si des détachements sont nécessaires... */

    if (g_arch_instruction_count_sources(first) == 0 && try->start_addr > 0)
    {
        prev = g_arch_instruction_get_prev_iter(instrs, first);
        g_arch_instruction_link_with(prev, first, ILT_EXEC_FLOW);
    }

    if (g_arch_instruction_count_sources(next) == 0 && (try->start_addr > 0 || try->insn_count > 0))
    {
        prev = g_arch_instruction_get_prev_iter(instrs, next);
        g_arch_instruction_link_with(prev, next, ILT_EXEC_FLOW);
    }

    /* Rattachements ? */

    if (handlers != NULL)
    {
        for (iter = first;
             iter != NULL;
             iter = g_arch_instruction_get_next_iter(instrs, iter, end))
        {
            if (g_arch_instruction_count_destinations(iter) == 0)
                continue;

            for (i = 0; i < count; i++)
                g_arch_instruction_link_with(iter, handlers[i].instr, ILT_CATCH_EXCEPTION);

        }

    }

 acc_exit:

    g_object_unref(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary   = représentation binaire à traiter.                 *
*                size     = nombre de groupe à parcourir.                     *
*                handlers = ensemble des groupes de gestionnaires.            *
*                count    = liste des quantités de gestionnaires groupés.     *
*                                                                             *
*  Description : Insère des indications dans le texte humainement lisibles.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mark_exception_handlers(const GLoadedBinary *binary, uleb128_t size, caught_exception **handlers, size_t *count)
{
    GCodeBuffer *buffer;                    /* Contenu textuel à modifier  */
    uleb128_t i;                            /* Boucle de parcours #1       */
    size_t j;                               /* Boucle de parcours #2       */
    GBufferLine *line;                      /* Nouvelle ligne à compléter  */
    size_t len;                             /* Taille de la description    */
    char *fulldesc;                         /* Description complète        */

    buffer = g_loaded_binary_get_disassembled_buffer(binary);

    for (i = 0; i < size; i++)
        for (j = 0; j < count[i]; j++)
        {
            line = g_code_buffer_insert_at(buffer, handlers[i][j].addr, true);
            g_buffer_line_start_merge_at(line, DLC_ASSEMBLY_HEAD);

            g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, "; ", 2, RTT_INDICATION, NULL);

            len = strlen(_("Handler for caught '%s'")) + strlen(handlers[i][j].desc);
            fulldesc = (char *)calloc(len + 1, sizeof(char));
            snprintf(fulldesc, len + 1, _("Handler for caught '%s'"), handlers[i][j].desc);

            g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, fulldesc, len, RTT_INDICATION, NULL);

            free(fulldesc);

        }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = représentation binaire à traiter.                  *
*                routine = routine associée, pour l'accès au instructions.    *
*                hlist   = liste de tous les gestionnaires en place.          *
*                count   = quantité de destinations trouvées. [OUT]           *
*                                                                             *
*  Description : Construit des listes pointant sur les différentes gestions.  *
*                                                                             *
*  Retour      : Adresses des codes à lier systématiquement.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static caught_exception **build_all_destinations_list(const GLoadedBinary *binary, const GBinRoutine *routine, const encoded_catch_handler_list *hlist, size_t **count)
{
    const mrange_t *range;                  /* Emplacement du symbole      */
    caught_exception **result;              /* Liste de listes à retourner */
    vmpa_t start;                           /* Début du code de la routine */
    GDexFormat *format;                     /* Format du binaire chargé    */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GArchInstruction *instrs;               /* Instructions Dalvik         */
    uleb128_t i;                            /* Boucle de parcours #1       */
    encoded_catch_handler *handlers;        /* Groupe de gestionnaires     */
    leb128_t max;                           /* Quantité d'exception        */
    leb128_t j;                             /* Boucle de parcours #2       */
    caught_exception *excep;                /* Raccourci confortable       */
    GDataType *type;                        /* Type de l'exception         */

    range = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

    start = get_mrange_addr(range)->virtual;

    format = G_DEX_FORMAT(g_loaded_binary_get_format(binary));

    proc = g_loaded_binary_get_processor(binary);
    instrs = NULL;//g_arch_processor_get_disassembled_instructions(proc);
    instrs = g_arch_instruction_find_by_address(instrs, start, true);

    /* Création d'un espace mémoire pour les listes */

    result = (caught_exception **)calloc(hlist->size, sizeof(caught_exception *));
    *count = (size_t *)calloc(hlist->size, sizeof(size_t));

    /* Parcours de chaque groupe de gestionnaires */

    for (i = 0; i < hlist->size; i++)
    {
        handlers = &hlist->list[i];
        max = leb128_abs(handlers->size);

        (*count)[i] = max + (handlers->size < 0 ? 1 : 0);
        result[i] = (caught_exception *)calloc((*count)[i], sizeof(caught_exception));

        (*count)[i] = 0;

        for (j = 0; j < max; j++)
        {
            excep = &result[i][(*count)[i]];

            excep->addr = start + handlers->handlers[j].addr * sizeof(uint16_t);
            excep->instr = g_arch_instruction_find_by_address(instrs, excep->addr, true);

            if (excep->instr == NULL)
                continue;

            type = get_type_from_dex_pool(format, handlers->handlers[j].type_idx);
            if (type == NULL)
                continue;

            excep->desc = g_data_type_to_string(type);
            g_object_unref(G_OBJECT(type));

            (*count)[i]++;

        }

        if (handlers->size < 0)
        {
            excep = &result[i][(*count)[i]];

            excep->addr = start + handlers->catch_all_addr * sizeof(uint16_t);
            excep->instr = g_arch_instruction_find_by_address(instrs, excep->addr, true);

            if (excep->instr != NULL)
            {
                excep->desc = strdup(_("default"));
                (*count)[i]++;
            }

        }

    }

    g_object_unref(G_OBJECT(proc));
    g_object_unref(G_OBJECT(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = représentation binaire à traiter.                   *
*                format = format du binaire Dex.                              *
*                method = méthode à analyser.                                 *
*                link   = édition de liens ou impression de commentaires ?    *
*                                                                             *
*  Description : Recherche et met en avant tous les gestionnaires d'exception.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void look_for_exception_handlers(const GLoadedBinary *binary, const GDexFormat *format, GDexMethod *method, bool link)
{
    const code_item *body;                  /* Description du corps        */
    GBinRoutine *routine;                   /* Abstraction globale         */
    encoded_catch_handler_list *hlist;      /* Confort vers la liste brute */
    caught_exception **handlers;            /* Interprétation des gestions */
    size_t *count;                          /* Tailles des groupes         */
    uint16_t i;                             /* Boucle de parcours #1       */
    try_item *try;                          /* Raccourci vers une zone     */
    uleb128_t index;                        /* Indice du bon gestionnaire  */
    size_t j;                               /* Boucle de parcours #2       */

    body = g_dex_method_get_dex_body(method);

    if (body == NULL)
        return;

    if (body->tries_size == 0)
        return;

    routine = g_dex_method_get_routine(method);

    hlist = body->handlers;
    handlers = build_all_destinations_list(binary, routine, hlist, &count);

    if (link)
        /* Pour chaque zone couverte... */
        for (i = 0; i < body->tries_size; i++)
        {
            try = &body->tries[i];

            if (!check_covered_area(try, routine))
                continue;

            for (index = 0; index < hlist->size; index++)
                if (try->handler_off == hlist->list[index].offset)
                    break;

            if (index == hlist->size)
                continue;

            attach_caught_code(binary, routine, try, handlers[index], count[index]);

        }

    else
        /* Ajout des précisions */
        mark_exception_handlers(binary, hlist->size, handlers, count);

    /* Libération de la mémoire utilisée */

    for (index = 0; index < hlist->size; index++)
    {
        for (j = 0; j < count[index]; j++)
            free(handlers[index][j].desc);

        if (handlers[index] != NULL)
            free(handlers[index]);

    }

    if (handlers != NULL) free(handlers);
    if (count != NULL) free(count);

    g_object_unref(G_OBJECT(routine));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = représentation binaire à traiter.                   *
*                link   = édition de liens ou impression de commentaires ?    *
*                                                                             *
*  Description : Traite tous les gestionnaires d'exception trouvés.           *
*                                                                             *
*  Retour      : true si une action a été menée, false sinon.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool process_exception_handlers(GLoadedBinary *binary, bool link)
{
    GDexFormat *format;                     /* Format du binaire chargé    */
    size_t cls_count;                       /* Nombre de classes trouvées  */
    size_t i;                               /* Boucle de parcours #1       */
    GDexClass *class;                       /* Classe à analyser           */
    size_t meth_count;                      /* Nombre de méthodes trouvées */
    size_t j;                               /* Boucle de parcours #2       */
    GDexMethod *method;                     /* Méthode à parcourir         */

    format = G_DEX_FORMAT(g_loaded_binary_get_format(binary));

    cls_count = g_dex_format_count_classes(format);
    for (i = 0; i < cls_count; i++)
    {
        class = g_dex_format_get_class(format, i);

        meth_count = g_dex_class_count_methods(class, false);
        for (j = 0; j < meth_count; j++)
        {
            method = g_dex_class_get_method(class, false, j);
            look_for_exception_handlers(binary, format, method, link);
            g_object_unref(G_OBJECT(method));
        }

        meth_count = g_dex_class_count_methods(class, true);
        for (j = 0; j < meth_count; j++)
        {
            method = g_dex_class_get_method(class, true, j);
            look_for_exception_handlers(binary, format, method, link);
            g_object_unref(G_OBJECT(method));
        }

        g_object_unref(G_OBJECT(class));

    }

    g_object_unref(G_OBJECT(format));

    return true;

}
