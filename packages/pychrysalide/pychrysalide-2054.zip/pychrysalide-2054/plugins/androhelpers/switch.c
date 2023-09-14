
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switch.c - apport de précisions sur les aiguillages Dalvik
 *
 * Copyright (C) 2012-2020 Cyrille Bagard
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


#include "switch.h"


#include <string.h>


#include <arch/dalvik/instruction.h>
#include <arch/dalvik/instruction-def.h>
#include <arch/operands/immediate.h>
#include <format/dex/dex-int.h>
#include <gtkext/gtkblockdisplay.h>
#include <../i18n.h>



/* Récupère les détails d'un aiguillage. */
static bool load_dex_switch(const GArchInstruction *, GArchInstruction *, const GDexFormat *, dex_switch *);

/* Lie les instructions selon les cas d'un aiguillage. */
static void link_all_switch_cases(GArchInstruction *, const dex_switch *, GArchInstruction *, vmpa_t, vmpa_t);

/* Prend en compte les absences de 'break' dans les cas. */
static void ensure_each_case_has_its_block(GArchInstruction *, GArchInstruction *);

/* Insère des indications dans le texte humainement lisibles. */
static void mark_all_switch_cases(const GArchInstruction *, const dex_switch *, GArchInstruction *, const GLoadedBinary *, vmpa_t, vmpa_t);

/* Recherche des aiguillages dans chaque instruction. */
static void look_for_switch_instructions(const GDexMethod *, GArchInstruction *, const GLoadedBinary *, const GDexFormat *, bool);



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'aiguillage rencontrée.               *
*                instrs  = liste des instructions pour tout le binaire.       *
*                format  = format du binaire Dex.                             *
*                dswitch = détails de l'aiguillage à reconstituer. [OUT]      *
*                                                                             *
*  Description : Récupère les détails d'un aiguillage.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_dex_switch(const GArchInstruction *instr, GArchInstruction *instrs, const GDexFormat *format, dex_switch *dswitch)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperand *operand;                  /* Operande à manipuler        */
    const GImmOperand *imm;                 /* Valeur concrête             */
    vmpa_t addr;                            /* Adresse du corps des infos  */
    GArchInstruction *info;                 /* Corps des infos brutes      */
    off_t pos;                              /* Position dans le binaire    */
    uint32_t *targets;                      /* Cibles relatives à corriger */
    uint16_t i;                             /* Boucle de parcours          */

    /* Récupération de l'opérande */

    operand = g_arch_instruction_get_operand(instr, 1);

    /*
    if (!G_IS_DALVIK_TARGET_OPERAND(operand))
        return false;
    */

    imm = NULL; //g_dalvik_target_operand_get_value(G_DALVIK_TARGET_OPERAND(operand));

    g_object_unref(G_OBJECT(operand));

    if (!g_imm_operand_to_vmpa_t(imm, &addr))
        return false;

    /* Lecture des détails */

    info = g_arch_instruction_find_by_address(instrs, addr, true);
    if (info == NULL)
        return false;

    g_arch_instruction_get_location(info, &pos, NULL, NULL);

    result = read_dex_switch(format, &pos, dswitch);

    /* Ajustement relatif */

    if (result)
    {
        g_arch_instruction_get_location(instr, NULL, NULL, &addr);

        if (dswitch->packed.ident == DPO_PACKED_SWITCH)
            targets = dswitch->packed.targets;
        else
            targets = dswitch->sparse.targets;

        for (i = 0; i < dswitch->packed.size; i++)
            targets[i] = ((uint32_t)addr) + targets[i] * sizeof(uint16_t);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'aiguillage rencontrée.               *
*                dswitch = détails de l'aiguillage à reconstituer.            *
*                instrs  = liste des instructions pour tout le binaire.       *
*                start   = début de la zone théoriquement couverte.           *
*                end     = fin de la zone théoriquement couverte.             *
*                                                                             *
*  Description : Lie les instructions selon les cas d'un aiguillage.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void link_all_switch_cases(GArchInstruction *instr, const dex_switch *dswitch, GArchInstruction *instrs, vmpa_t start, vmpa_t end)
{
    uint32_t *targets;                      /* Cibles relatives à corriger */
    uint16_t i;                             /* Boucle de parcours          */
    GArchInstruction *next;                 /* Instruction suivante        */
    uint32_t value;                         /* Valeur à indiquer           */
    GArchOperand *imm;                      /* Forme de la valeur reconnue */

    /* Valeurs définies */

    if (dswitch->packed.ident == DPO_PACKED_SWITCH)
        targets = dswitch->packed.targets;
    else
        targets = dswitch->sparse.targets;

    for (i = 0; i < dswitch->packed.size; i++)
    {
        if (!(start <= targets[i] && targets[i] < end))
            continue;

        next = g_arch_instruction_find_by_address(instrs, (vmpa_t)targets[i], true);

        if (next != NULL)
        {
            if (dswitch->packed.ident == DPO_PACKED_SWITCH)
                value = dswitch->packed.first_key + i;
            else
                value = dswitch->sparse.keys[i];

            imm = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, value);
            g_arch_instruction_link_with(instr, next, ILT_CASE_JUMP);
            ensure_each_case_has_its_block(next, instrs);

        }

    }

    /* Cas du défaut */

    next = g_arch_instruction_get_next_iter(instrs, instr, end);

    if (next != NULL)
    {
        g_arch_instruction_link_with(instr, next, ILT_CASE_JUMP);
        ensure_each_case_has_its_block(next, instrs);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'aiguillage rencontrée.               *
*                instrs  = liste des instructions pour tout le binaire.       *
*                                                                             *
*  Description : Prend en compte les absences de 'break' dans les cas.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void ensure_each_case_has_its_block(GArchInstruction *instr, GArchInstruction *instrs)
{
    GArchInstruction *prev;                 /* Instruction avant un cas    */

    /**
     * La situation où un cas n'a pas de 'break' conduit à une fusion du corps
     * du cas avec le corps du cas suivant (partie commune).
     * La fin du premier cas n'ayant pas de saut enregistré, rien n'entraîne un
     * lien logique, et donc une séparation des deux cas en blocs distincts.
     *
     * Cette procédure établit les vérifications nécessaires, et rétablit
     * la logique des liens et des blocs en cas de besoin.
     */

    prev = g_arch_instruction_get_prev_iter(instrs, instr);

    if (prev != NULL
        && g_arch_instruction_count_destinations(prev) == 0
        && !(g_arch_instruction_get_flags(prev) & AIF_RETURN_POINT))
    {
        g_arch_instruction_link_with(prev, instr, ILT_EXEC_FLOW);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'aiguillage rencontrée.               *
*                dswitch = détails de l'aiguillage à reconstituer.            *
*                instrs  = liste des instructions pour tout le binaire.       *
*                binary  = représentation binaire à traiter.                  *
*                start   = début de la zone théoriquement couverte.           *
*                end     = fin de la zone théoriquement couverte.             *
*                                                                             *
*  Description : Insère des indications dans le texte humainement lisibles.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mark_all_switch_cases(const GArchInstruction *instr, const dex_switch *dswitch, GArchInstruction *instrs, const GLoadedBinary *binary, vmpa_t start, vmpa_t end)
{
    GCodeBuffer *buffer;                    /* Contenu textuel à modifier  */
    uint32_t *targets;                      /* Cibles relatives à corriger */
    uint16_t i;                             /* Boucle de parcours          */
    uint16_t index;                         /* Véritable indice recalculé  */
    uint32_t value;                         /* Valeur à indiquer           */
    GBufferLine *line;                      /* Nouvelle ligne à compléter  */
    size_t len;                             /* Taille de la description    */
    char *fulldesc;                         /* Description complète        */
    GArchInstruction *next;                 /* Instruction suivante        */
    vmpa_t addr;                            /* Adresse de cette instruction*/

    buffer = g_loaded_binary_get_disassembled_buffer(binary);

    /* Valeurs définies */

    if (dswitch->packed.ident == DPO_PACKED_SWITCH)
        targets = dswitch->packed.targets;
    else
        targets = dswitch->sparse.targets;

    for (i = dswitch->packed.size; i > 0; i--)
    {
        index = i - 1;

        if (!(start <= targets[index] && targets[index] < end))
            continue;

        if (dswitch->packed.ident == DPO_PACKED_SWITCH)
            value = dswitch->packed.first_key + index;
        else
            value = dswitch->sparse.keys[index];

        line = g_code_buffer_insert_at(buffer, (vmpa_t)targets[index], true);
        g_buffer_line_start_merge_at(line, DLC_ASSEMBLY_HEAD);

        len = strlen(_("; Case for value 0x%08x (%d)")) + 8 + strlen("4294967295U") /* UINT_MAX */;
        fulldesc = (char *)calloc(len + 1, sizeof(char));
        len = snprintf(fulldesc, len + 1, _("; Case for value 0x%08x (%d)"), value, value);

        g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD, fulldesc, len, RTT_INDICATION, NULL);

        free(fulldesc);

    }

    /* Cas du défaut */

    next = g_arch_instruction_get_next_iter(instrs, instr, end);

    if (next != NULL)
    {
        g_arch_instruction_get_location(next, NULL, NULL, &addr);

        line = g_code_buffer_insert_at(buffer, addr, true);
        g_buffer_line_start_merge_at(line, DLC_ASSEMBLY_HEAD);

        fulldesc = _("; Default case");
        g_buffer_line_append_text(line, DLC_ASSEMBLY_HEAD,
                                  fulldesc, strlen(fulldesc), RTT_INDICATION, NULL);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : method = routine à venir parcourir.                          *
*                instrs = liste des instructions pour tout le binaire.        *
*                binary = représentation binaire à traiter.                   *
*                format = format du binaire Dex.                              *
*                link   = édition de liens ou impression de commentaires ?    *
*                                                                             *
*  Description : Recherche des aiguillages dans chaque instruction.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void look_for_switch_instructions(const GDexMethod *method, GArchInstruction *instrs, const GLoadedBinary *binary, const GDexFormat *format, bool link)
{
    GBinRoutine *routine;                   /* Abstraction de la méthode   */
    const mrange_t *range;                  /* Emplacement du symbole      */
    vmpa_t start;                           /* Début de la zone couverte   */
    vmpa_t end;                             /* Fin de la zone couverte     */
    GArchInstruction *iter;                 /* Boucle de parcours          */
    DalvikOpcodes opcode;                   /* Type d'instruction Dalvik   */
    dex_switch dswitch;                     /* Infos d'aiguillage          */

    routine = g_dex_method_get_routine(method);
    range = g_binary_symbol_get_range(G_BIN_SYMBOL(routine));

    start = get_mrange_addr(range)->virtual;
    end = start + get_mrange_length(range);

    g_object_unref(G_OBJECT(routine));

    for (iter = g_arch_instruction_find_by_address(instrs, start, true);
         iter != NULL;
         iter = g_arch_instruction_get_next_iter(instrs, iter, end))
    {
        if (!G_IS_DALVIK_INSTRUCTION(iter))
            continue;

        opcode = g_dalvik_instruction_get_opcode(G_DALVIK_INSTRUCTION(iter));

        if (opcode != DOP_PACKED_SWITCH && opcode != DOP_SPARSE_SWITCH)
            continue;

        if (!load_dex_switch(iter, instrs, format, &dswitch))
            continue;

        if (link)
            link_all_switch_cases(iter, &dswitch, instrs, start, end);
        else
            mark_all_switch_cases(iter, &dswitch, instrs, binary, start, end);

        reset_dex_switch(&dswitch);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = représentation binaire à traiter.                   *
*                link   = édition de liens ou impression de commentaires ?    *
*                                                                             *
*  Description : Traite les données binaires associées aux switchs.           *
*                                                                             *
*  Retour      : true si une action a été menée, false sinon.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool extract_switch_info(GLoadedBinary *binary, bool link)
{
    GDexFormat *format;                     /* Format du binaire chargé    */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GArchInstruction *instrs;               /* Instructions Dalvik         */
    size_t cls_count;                       /* Nombre de classes trouvées  */
    size_t i;                               /* Boucle de parcours #1       */
    GDexClass *class;                       /* Classe à analyser           */
    size_t meth_count;                      /* Nombre de méthodes trouvées */
    size_t j;                               /* Boucle de parcours #2       */
    GDexMethod *method;                     /* Méthode à parcourir         */

    format = G_DEX_FORMAT(g_loaded_binary_get_format(binary));
    proc = g_loaded_binary_get_processor(binary);
    instrs = NULL;//g_arch_processor_get_disassembled_instructions(proc);

    cls_count = g_dex_format_count_classes(format);
    for (i = 0; i < cls_count; i++)
    {
        class = g_dex_format_get_class(format, i);

        meth_count = g_dex_class_count_methods(class, false);
        for (j = 0; j < meth_count; j++)
        {
            method = g_dex_class_get_method(class, false, j);
            look_for_switch_instructions(method, instrs, binary, format, link);
            g_object_unref(G_OBJECT(method));
        }

        meth_count = g_dex_class_count_methods(class, true);
        for (j = 0; j < meth_count; j++)
        {
            method = g_dex_class_get_method(class, true, j);
            look_for_switch_instructions(method, instrs, binary, format, link);
            g_object_unref(G_OBJECT(method));
        }

        g_object_unref(G_OBJECT(class));

    }

    g_object_unref(G_OBJECT(proc));
    g_object_unref(G_OBJECT(format));

    return true;

}
