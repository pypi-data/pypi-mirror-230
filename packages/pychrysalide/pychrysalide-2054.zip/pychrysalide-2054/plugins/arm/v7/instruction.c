
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - gestion des instructions ARMv7
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


#include "instruction.h"


#include <assert.h>
#ifndef NDEBUG
#   include <string.h>
#endif


#include <common/extstr.h>


#include "opcodes/hooks.h"
#include "opcodes/keywords.h"
#include "../instruction-int.h"



/* Définition d'une instruction d'architecture ARMv7 (instance) */
struct _GArmV7Instruction
{
    GArmInstruction parent;                 /* Instance parente            */

    ARMv7Syntax sid;                        /* Forme de syntaxe            */
    char encoding;                          /* Encodage de l'instruction   */

    bool setflags;                          /* Mise à jour des drapeaux    */

};


/* Définition d'une instruction d'architecture ARMv7 (classe) */
struct _GArmV7InstructionClass
{
    GArmInstructionClass parent;            /* Classe parente              */

};


/* Initialise la classe des instructions ARMv7. */
static void g_armv7_instruction_class_init(GArmV7InstructionClass *);

/* Initialise une instance d'instruction ARMv7. */
static void g_armv7_instruction_init(GArmV7Instruction *);

/* Supprime toutes les références externes. */
static void g_armv7_instruction_dispose(GArmV7Instruction *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_instruction_finalize(GArmV7Instruction *);

/* Indique l'encodage d'une instruction de façon détaillée. */
static const char *g_armv7_instruction_get_encoding(const GArmV7Instruction *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *g_armv7_instruction_get_keyword(const GArmV7Instruction *);

/* Complète un désassemblage accompli pour une instruction. */
static void g_armv7_instruction_call_hook(GArmV7Instruction *, InstrProcessHook, GArchProcessor *, GProcContext *, GExeFormat *);

/* Construit un petit résumé concis de l'instruction. */
static char *g_armv7_instruction_build_tooltip(const GArmV7Instruction *);



/* -------------------- CONSERVATION SUR DISQUE DES INSTRUCTIONS -------------------- */


/* Charge une instruction depuis une mémoire tampon. */
static bool g_armv7_instruction_unserialize(GArmV7Instruction *, GAsmStorage *, GBinFormat *, packed_buffer_t *);

/* Sauvegarde une instruction dans une mémoire tampon. */
static bool g_armv7_instruction_serialize(GArmV7Instruction *, GAsmStorage *, packed_buffer_t *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_instruction_load(GArmV7Instruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_instruction_store(GArmV7Instruction *, GObjectStorage *, packed_buffer_t *);



/* Indique le type défini pour une représentation d'une instruction ARMv7. */
G_DEFINE_TYPE(GArmV7Instruction, g_armv7_instruction, G_TYPE_ARM_INSTRUCTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instructions ARMv7.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_instruction_class_init(GArmV7InstructionClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    object_class = G_OBJECT_CLASS(klass);
    instr = G_ARCH_INSTRUCTION_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_instruction_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_armv7_instruction_finalize;

    instr->get_encoding = (get_instruction_encoding_fc)g_armv7_instruction_get_encoding;
    instr->get_keyword = (get_instruction_keyword_fc)g_armv7_instruction_get_keyword;
    instr->call_hook = (call_instruction_hook_fc)g_armv7_instruction_call_hook;
    instr->build_tooltip = (build_instruction_tooltip_fc)g_armv7_instruction_build_tooltip;

    instr->unserialize = (unserialize_instruction_fc)g_armv7_instruction_unserialize;
    instr->serialize = (serialize_instruction_fc)g_armv7_instruction_serialize;

    instr->load = (load_instruction_fc)g_armv7_instruction_load;
    instr->store = (store_instruction_fc)g_armv7_instruction_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'instruction ARMv7.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_instruction_init(GArmV7Instruction *instr)
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

static void g_armv7_instruction_dispose(GArmV7Instruction *instr)
{
    G_OBJECT_CLASS(g_armv7_instruction_parent_class)->dispose(G_OBJECT(instr));

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

static void g_armv7_instruction_finalize(GArmV7Instruction *instr)
{
    G_OBJECT_CLASS(g_armv7_instruction_parent_class)->finalize(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : uid = identifiant unique attribué à l'instruction.           *
*                sid = identifiant unique attribué à sa forme de syntaxe.     *
*                                                                             *
*  Description : Crée une instruction pour l'architecture ARMv7.              *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_armv7_instruction_new(itid_t uid, ARMv7Syntax sid)
{
    GArmV7Instruction *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_ARMV7_INSTRUCTION, NULL);

    g_arch_instruction_set_unique_id(G_ARCH_INSTRUCTION(result), uid);

    result->sid = sid;

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

static const char *g_armv7_instruction_get_encoding(const GArmV7Instruction *instr)
{
    const char *result;                     /* Description à retourner     */

    switch (instr->encoding)
    {
        case 't':
            result = "Thumb/16";
            break;

        case 'T':
            result = "Thumb/32";
            break;

        default:
            result = "ARM";
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr    = instruction quelconque à modifier.                *
*                encoding = encodage de l'instruction.                        *
*                                                                             *
*  Description : Précise l'encodage d'une instruction ARMv7 dans le détail.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_armv7_instruction_set_encoding(GArmV7Instruction *instr, const char *encoding)
{
    assert(strlen(encoding) == 1);
    assert(encoding[0] == 'A' || encoding[0] == 'T' || encoding[0] == 't');

    instr->encoding = encoding[0];

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

static const char *g_armv7_instruction_get_keyword(const GArmV7Instruction *instr)
{
    const char *result;                     /* Désignation à retourner     */
    GArmInstruction *parent;                /* Autre forme de l'instance   */

    parent = G_ARM_INSTRUCTION(instr);

    assert(instr->sid < AOP7_ENC_COUNT);

    if (parent->suffix == NULL)
        result = _armv7_keywords[instr->sid];

    else
    {
        if (parent->cached_keyword == NULL)
        {
            parent->cached_keyword = strdup(_armv7_keywords[instr->sid]);
            parent->cached_keyword = stradd(parent->cached_keyword, parent->suffix);
        }

        result = parent->cached_keyword;

    }

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

static void g_armv7_instruction_call_hook(GArmV7Instruction *instr, InstrProcessHook type, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    instr_hook_fc hook;                     /* Décrochage à appeler        */

    assert(type < IPH_COUNT);

    assert(instr->sid < AOP7_ENC_COUNT);

    hook = _armv7_hooks[instr->sid][type];

    if (hook != NULL)
        hook(G_ARCH_INSTRUCTION(instr), proc, context, format);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction Dalvik à consulter.                      *
*                                                                             *
*  Description : Construit un petit résumé concis de l'instruction.           *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_armv7_instruction_build_tooltip(const GArmV7Instruction *instr)
{
    char *result;                           /* Description à retourner     */

    result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction ARMv7 à mettre à jour.                   *
*                set   = statut à enregistrer.                                *
*                                                                             *
*  Description : Définit si une instruction ARMv7 met à jour les drapeaux.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_armv7_instruction_define_setflags(GArmV7Instruction *instr, bool set)
{
    instr->setflags = set;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction ARMv7 à consulter.                       *
*                                                                             *
*  Description : Indique si une instruction ARMv7 met à jour les drapeaux.    *
*                                                                             *
*  Retour      : Statut des incidences de l'instruction.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_armv7_instruction_get_setflags(const GArmV7Instruction *instr)
{
    return instr->setflags;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION SUR DISQUE DES INSTRUCTIONS                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à consulter.              *
*                storage = mécanisme de sauvegarde à manipuler.               *
*                format  = format binaire chargé associé à l'architecture.    *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Charge une instruction depuis une mémoire tampon.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_armv7_instruction_unserialize(GArmV7Instruction *instr, GAsmStorage *storage, GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    uint8_t boolean;                        /* Valeur booléenne            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_armv7_instruction_parent_class);

    result = parent->unserialize(G_ARCH_INSTRUCTION(instr), storage, format, pbuf);

    if (result)
        result = extract_packed_buffer(pbuf, &instr->sid, sizeof(ARMv7Syntax), true);

    if (result)
        result = extract_packed_buffer(pbuf, &instr->encoding, sizeof(char), false);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);

        if (result)
            instr->setflags = (boolean == 1 ? true : false);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction d'assemblage à consulter.              *
*                storage = mécanisme de sauvegarde à manipuler.               *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde une instruction dans une mémoire tampon.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_armv7_instruction_serialize(GArmV7Instruction *instr, GAsmStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    uint8_t boolean;                        /* Valeur booléenne            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_armv7_instruction_parent_class);

    result = parent->serialize(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, &instr->sid, sizeof(ARMv7Syntax), true);

    if (result)
        result = extend_packed_buffer(pbuf, &instr->encoding, sizeof(char), false);

    if (result)
    {
        boolean = (instr->setflags ? 1 : 0);
        result = extend_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);
    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_armv7_instruction_load(GArmV7Instruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    uint8_t boolean;                        /* Valeur booléenne            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_armv7_instruction_parent_class);

    result = parent->load(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
        result = unpack_uleb128(&value, pbuf);

    if (result)
        instr->sid = value;

    if (result)
        result = extract_packed_buffer(pbuf, &instr->encoding, sizeof(char), false);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);

        if (result)
            instr->setflags = (boolean == 1 ? true : false);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_armv7_instruction_store(GArmV7Instruction *instr, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstructionClass *parent;          /* Classe parente à consulter  */
    uint8_t boolean;                        /* Valeur booléenne            */

    parent = G_ARCH_INSTRUCTION_CLASS(g_armv7_instruction_parent_class);

    result = parent->store(G_ARCH_INSTRUCTION(instr), storage, pbuf);

    if (result)
        result = pack_uleb128((uleb128_t []){ instr->sid }, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, &instr->encoding, sizeof(char), false);

    if (result)
    {
        boolean = (instr->setflags ? 1 : 0);
        result = extend_packed_buffer(pbuf, &boolean, sizeof(uint8_t), false);
    }

    return result;

}
