
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - prototypes pour la gestion générique des instructions
 *
 * Copyright (C) 2008-2020 Cyrille Bagard
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


#ifndef _ARCH_INSTRUCTION_H
#define _ARCH_INSTRUCTION_H


#include <sys/types.h>


#include "context.h"
#include "operand.h"
#include "register.h"
#include "vmpa.h"
#include "../analysis/type.h"
#include "../common/packed.h"
#include "../format/executable.h"



#define G_TYPE_ARCH_INSTRUCTION            g_arch_instruction_get_type()
#define G_ARCH_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), g_arch_instruction_get_type(), GArchInstruction))
#define G_IS_ARCH_INSTRUCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_arch_instruction_get_type()))
#define G_ARCH_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARCH_INSTRUCTION, GArchInstructionClass))
#define G_IS_ARCH_INSTRUCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARCH_INSTRUCTION))
#define G_ARCH_INSTRUCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARCH_INSTRUCTION, GArchInstructionClass))


/* Définition générique d'une instruction d'architecture (instance) */
typedef struct _GArchInstruction GArchInstruction;

/* Définition générique d'une instruction d'architecture (classe) */
typedef struct _GArchInstructionClass GArchInstructionClass;


/* Drapeaux pour informations complémentaires */

#define AIF_USER_BIT 4

typedef enum _ArchInstrFlag
{
    AIF_NONE              = (0 << 0),       /* Aucune information          */
    AIF_ROUTINE_START     = (1 << 0),       /* Début de routine            */
    AIF_RETURN_POINT      = (1 << 1),       /* Retour de fonction appelée  */
    AIF_COND_RETURN_POINT = (1 << 2),       /* Retour éventuel de fonction */
    AIF_CALL              = (1 << 3),       /* Instruction d'appel         */

    AIF_LOW_USER          = (1 << AIF_USER_BIT), /* Premier bit disponible */
    AIF_HIGH_USER         = (1 << 7),      /* Dernier bit disponible      */

} ArchInstrFlag;

/* Type pour les types d'instructions */
typedef uint16_t itid_t;

/* Types de crochet de traitement */
typedef enum _InstrProcessHook
{
    IPH_FETCH,                              /* Itinéraire de désassemblage */
    IPH_LINK,                               /* Edition des liens           */
    IPH_POST,                               /* Résolution des symboles     */

    IPH_COUNT

} InstrProcessHook;


/* Indique le type défini pour une instruction d'architecture. */
GType g_arch_instruction_get_type(void);

/* Indique l'encodage d'une instruction de façon détaillée. */
const char *g_arch_instruction_get_encoding(const GArchInstruction *);

/* Ajoute une information complémentaire à une instruction. */
bool g_arch_instruction_set_flag(GArchInstruction *, ArchInstrFlag);

/* Retire une information complémentaire à une instruction. */
bool g_arch_instruction_unset_flag(GArchInstruction *, ArchInstrFlag);

/* Détermine si une instruction possède un fanion particulier. */
bool g_arch_instruction_has_flag(const GArchInstruction *, ArchInstrFlag);

/* Fournit les informations complémentaires d'une instruction. */
ArchInstrFlag g_arch_instruction_get_flags(const GArchInstruction *);

/* Définit l'identifiant unique pour un ensemble d'instructions. */
void g_arch_instruction_set_unique_id(GArchInstruction *, itid_t);

/* Fournit l'identifiant unique pour un ensemble d'instructions. */
itid_t g_arch_instruction_get_unique_id(const GArchInstruction *);


/**
 * La définition de "GArchProcessor", utile aux traitements complémentaires, ne peut
 * se faire en incluant le fichier d'en-tête "processor.h", pour cause de références
 * circulaires.
 *
 * On procède donc à une seconde déclaration, en attendant éventuellement mieux.
 */

/* Depuis "processeur.h" : définition générique d'un processeur d'architecture (instance) */
typedef struct _GArchProcessor GArchProcessor;


/* Complète un désassemblage accompli pour une instruction. */
typedef void (* instr_hook_fc) (GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);

/* Complète un désassemblage accompli pour une instruction. */
void g_arch_instruction_call_hook(GArchInstruction *, InstrProcessHook, GArchProcessor *, GProcContext *, GExeFormat *);

/* Définit la localisation d'une instruction. */
void g_arch_instruction_set_range(GArchInstruction *, const mrange_t *);

/* Fournit la place mémoire d'une instruction. */
const mrange_t *g_arch_instruction_get_range(const GArchInstruction *);



/* Fournit la localisation d'une instruction. */
void g_arch_instruction_get_location(const GArchInstruction *, off_t *, off_t *, vmpa_t *) __attribute__ ((deprecated));



/* Liste les registres lus et écrits par l'instruction. */
void g_arch_instruction_get_rw_registers(const GArchInstruction *, GArchRegister ***, size_t *, GArchRegister ***, size_t *) __attribute__ ((deprecated));



/* --------------------------- MANIPULATION DES OPERANDES --------------------------- */


/* Verrouille les accès à la liste des opérandes. */
void g_arch_instruction_lock_operands(GArchInstruction *);

/* Déverrouille les accès à la liste des opérandes. */
void g_arch_instruction_unlock_operands(GArchInstruction *);

/* Attache un opérande supplémentaire à une instruction. */
void g_arch_instruction_attach_extra_operand(GArchInstruction *, GArchOperand *);

/* Indique la quantité d'opérandes présents dans l'instruction. */
size_t _g_arch_instruction_count_operands(const GArchInstruction *);

/* Fournit un opérande donné d'une instruction. */
GArchOperand *_g_arch_instruction_get_operand(const GArchInstruction *, size_t);

/* Remplace un opérande d'une instruction par un autre. */
bool _g_arch_instruction_replace_operand(GArchInstruction *, GArchOperand *, GArchOperand *);

/* Détache un opérande liée d'une instruction. */
bool _g_arch_instruction_detach_operand(GArchInstruction *, GArchOperand *);


#define g_arch_instruction_count_operands(ins)                      \
    ({                                                              \
        size_t __result;                                            \
        g_arch_instruction_lock_operands(ins);                      \
        __result = _g_arch_instruction_count_operands(ins);         \
        g_arch_instruction_unlock_operands(ins);                    \
        __result;                                                   \
    })

#define g_arch_instruction_get_operand(ins, idx)                    \
    ({                                                              \
        GArchOperand *__result;                                     \
        g_arch_instruction_lock_operands(ins);                      \
        __result = _g_arch_instruction_get_operand(ins, idx);       \
        g_arch_instruction_unlock_operands(ins);                    \
        __result;                                                   \
    })

#define g_arch_instruction_replace_operand(ins, o, n)               \
    ({                                                              \
        bool __result;                                              \
        g_arch_instruction_lock_operands(ins);                      \
        __result = _g_arch_instruction_replace_operand(ins, o, n);  \
        g_arch_instruction_unlock_operands(ins);                    \
        __result;                                                   \
    })

#define g_arch_instruction_detach_operand(ins, o)                   \
    ({                                                              \
        bool __result;                                              \
        g_arch_instruction_lock_operands(ins);                      \
        __result = _g_arch_instruction_detach_operand(ins, o);      \
        g_arch_instruction_unlock_operands(ins);                    \
        __result;                                                   \
    })


/* Détermine le chemin conduisant à un opérande. */
char *g_arch_instruction_find_operand_path(GArchInstruction *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
GArchOperand *g_arch_instruction_get_operand_from_path(GArchInstruction *, const char *);



/* ------------------- DEFINITION DES LIAISONS ENTRE INSTRUCTIONS ------------------- */


/* Typage des instructions rencontrées */
typedef enum _InstructionLinkType
{
    ILT_EXEC_FLOW,                          /* Raccord attendu entre blocs */
    ILT_JUMP,                               /* Saut inconditionnel         */
    ILT_CASE_JUMP,                          /* Saut suite à aiguillage     */
    ILT_JUMP_IF_TRUE,                       /* Saut conditionnel (si vrai) */
    ILT_JUMP_IF_FALSE,                      /* Saut conditionnel (si faux) */
    ILT_LOOP,                               /* Retour en arrière (boucle)  */
    ILT_CALL,                               /* Appel d'une fonction        */
    ILT_CATCH_EXCEPTION,                    /* Gestion d'une exception     */
    ILT_REF,                                /* Simple référence croisée    */

    ILT_COUNT

} InstructionLinkType;

/* Déscription d'une liaison entre deux instructions */
typedef struct _instr_link_t
{
    GArchInstruction *linked;               /* Autre instruction liée      */
    InstructionLinkType type;               /* Type de liaison             */

} instr_link_t;


#define ref_instr_link(l) g_object_ref(G_OBJECT(l->linked));
#define unref_instr_link(l) g_object_unref(G_OBJECT(l->linked));


/* Met à disposition un encadrement des accès aux liens. */
void g_arch_instruction_lock_unlock_links(GArchInstruction *, bool, bool);

/* Détermine si un type de lien existe dans une instruction. */
bool g_arch_instruction_has_link(GArchInstruction *, InstructionLinkType);

/* Détermine si un lien est déjà établi entre deux instructions. */
bool g_arch_instruction_has_link_to(GArchInstruction *, const GArchInstruction *);

/* Etablit un lien entre deux instructions. */
void g_arch_instruction_link_with(GArchInstruction *, GArchInstruction *, InstructionLinkType);

/* Change la nature d'un lien entre deux instructions. */
bool g_arch_instruction_change_link(GArchInstruction *, GArchInstruction *, InstructionLinkType, InstructionLinkType);

/* Supprime tous les liens établis avec d'autres instructions. */
void g_arch_instruction_delete_all_links(GArchInstruction *);

#define g_arch_instruction_lock_src(ins) g_arch_instruction_lock_unlock_links(ins, true, true)
#define g_arch_instruction_unlock_src(ins) g_arch_instruction_lock_unlock_links(ins, true, false)

/* Fournit la quantité d'instructions pointant vers une autre. */
size_t g_arch_instruction_count_sources(const GArchInstruction *);

/* Fournit les détails d'une origine d'une instruction donnée. */
const instr_link_t *g_arch_instruction_get_source(GArchInstruction *, size_t);

/* Fournit tous les détails d'origine d'une instruction donnée. */
instr_link_t *g_arch_instruction_get_sources(GArchInstruction *, size_t *);

#define g_arch_instruction_lock_dest(ins) g_arch_instruction_lock_unlock_links(ins, false, true)
#define g_arch_instruction_unlock_dest(ins) g_arch_instruction_lock_unlock_links(ins, false, false)

/* Donne le nombre d'instructions non naturellement suivantes. */
size_t g_arch_instruction_count_destinations(const GArchInstruction *);

/* Fournit les détails d'une destination d'une instruction. */
const instr_link_t *g_arch_instruction_get_destination(GArchInstruction *, size_t);

/* Fournit la destination d'une instruction et d'un type donné. */
GArchInstruction *g_arch_instruction_get_given_destination(GArchInstruction *, InstructionLinkType);

/* Fournit tous les détails de destination d'une instruction. */
instr_link_t *g_arch_instruction_get_destinations(GArchInstruction *, size_t *);



/* --------------------- CONVERSIONS DU FORMAT DES INSTRUCTIONS --------------------- */


/* Fournit le nom humain de l'instruction manipulée. */
const char *g_arch_instruction_get_keyword(GArchInstruction *);

/* Construit un petit résumé concis de l'instruction. */
char *g_arch_instruction_build_tooltip(const GArchInstruction *);

/* Fournit une description pour l'instruction manipulée. */
const char *g_arch_instruction_get_description(const GArchInstruction *);



#endif  /* _ARCH_INSTRUCTION_H */
