
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - gestion des instructions de la VM Dalvik v35
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "instruction.h"


#include <assert.h>


#include "opcodes/descriptions.h"
#include "opcodes/hooks.h"
#include "opcodes/keywords.h"
#include "../instruction-int.h"



/* Définition générique d'une instruction d'architecture Dalvik v35 (instance) */
struct _GDalvik35Instruction
{
    GDalvikInstruction parent;              /* A laisser en premier        */

};

/* Définition générique d'une instruction d'architecture Dalvik v35 (classe) */
struct _GDalvik35InstructionClass
{
    GDalvikInstructionClass parent;         /* A laisser en premier        */

};


/* Initialise la classe des instructions pour Dalvik v35. */
static void g_dalvik35_instruction_class_init(GDalvik35InstructionClass *);

/* Initialise une instance d'opérande d'architecture Dalvik. */
static void g_dalvik35_instruction_init(GDalvik35Instruction *);

/* Supprime toutes les références externes. */
static void g_dalvik35_instruction_dispose(GDalvik35Instruction *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik35_instruction_finalize(GDalvik35Instruction *);

/* Indique l'encodage d'une instruction de façon détaillée. */
static const char *g_dalvik35_instruction_get_encoding(const GDalvik35Instruction *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *g_dalvik35_instruction_get_keyword(const GDalvik35Instruction *);

/* Complète un désassemblage accompli pour une instruction. */
static void g_dalvik35_instruction_call_hook(GDalvik35Instruction *, InstrProcessHook, GArchProcessor *, GProcContext *, GExeFormat *);

/* Fournit une description pour l'instruction manipulée. */
static const char *g_dalvik35_instruction_get_description(const GDalvik35Instruction *);



/* Indique le type défini pour une instruction d'architecture Dalvik v35. */
G_DEFINE_TYPE(GDalvik35Instruction, g_dalvik35_instruction, G_TYPE_DALVIK_INSTRUCTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions pour Dalvik v35.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_instruction_class_init(GDalvik35InstructionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik35_instruction_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik35_instruction_finalize;

    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    instr->get_encoding = (get_instruction_encoding_fc)g_dalvik35_instruction_get_encoding;
    instr->get_keyword = (get_instruction_keyword_fc)g_dalvik35_instruction_get_keyword;
    instr->call_hook = (call_instruction_hook_fc)g_dalvik35_instruction_call_hook;
    instr->get_desc = (get_instruction_desc_fc)g_dalvik35_instruction_get_description;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction d'architecture Dalvik. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_instruction_init(GDalvik35Instruction *instr)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_instruction_dispose(GDalvik35Instruction *instr)
{
    G_OBJECT_CLASS(g_dalvik35_instruction_parent_class)->dispose(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_instruction_finalize(GDalvik35Instruction *instr)
{
    G_OBJECT_CLASS(g_dalvik35_instruction_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : uid = identifiant unique attribué à l'instruction.           *
*                                                                             *
*  Description : Crée une instruction pour l'architecture Dalvik v35.         *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_dalvik35_instruction_new(itid_t uid)
{
    GDalvik35Instruction *result;           /* Structure à retourner       */

    result = g_object_new(G_TYPE_DALVIK35_INSTRUCTION, NULL);

    g_arch_instruction_set_unique_id(G_ARCH_INSTRUCTION(result), uid);

    return G_ARCH_INSTRUCTION(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction quelconque à consulter.                  *
*                                                                             *
*  Description : Indique l'encodage d'une instruction de façon détaillée.     *
*                                                                             *
*  Retour      : Description humaine de l'encodage utilisé.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_dalvik35_instruction_get_encoding(const GDalvik35Instruction *instr)
{
    const char *result;                     /* Description à retourner     */

    result = "Dalvik v35";

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction d'assemblage à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'instruction manipulée.            *
*                                                                             *
*  Retour      : Mot clef de bas niveau.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_dalvik35_instruction_get_keyword(const GDalvik35Instruction *instr)
{
    const char *result;                     /* Désignation à retourner     */
    itid_t uid;                             /* Accès simplifié             */

    uid = g_arch_instruction_get_unique_id(G_ARCH_INSTRUCTION(instr));

    assert(uid < DOP35_COUNT);

    result = _dalvik35_keywords[uid];

    if (result == NULL)
        result = "unused";

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction quelconque à traiter.                  *
*                type    = type de procédure à utiliser.                      *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = accès aux données du binaire d'origine.            *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik35_instruction_call_hook(GDalvik35Instruction *instr, InstrProcessHook type, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchInstruction *base;                 /* Version de base d'instance  */
    itid_t uid;                             /* Accès simplifié             */
    instr_hook_fc hook;                     /* Décrochage à appeler        */

    assert(type < IPH_COUNT);

    base = G_ARCH_INSTRUCTION(instr);

    uid = g_arch_instruction_get_unique_id(base);

    assert(uid < DOP35_COUNT);

    hook = _dalvik35_hooks[uid][type];

    if (hook != NULL)
        hook(base, proc, context, format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction d'assemblage à consulter.                *
*                                                                             *
*  Description : Fournit une description pour l'instruction manipulée.        *
*                                                                             *
*  Retour      : Chaîne de caractères avec balises éventuelles.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_dalvik35_instruction_get_description(const GDalvik35Instruction *instr)
{
    const char *result;                     /* Description à retourner     */
    itid_t uid;                             /* Accès simplifié             */

    uid = g_arch_instruction_get_unique_id(G_ARCH_INSTRUCTION(instr));

    assert(uid < DOP35_COUNT);

    result = _dalvik35_descriptions[uid];

    return result;

}
