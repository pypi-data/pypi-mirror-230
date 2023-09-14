
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction-int.h - prototypes pour la définition générique interne des instructions
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


#ifndef _ARCH_INSTRUCTION_INT_H
#define _ARCH_INSTRUCTION_INT_H


#include "instruction.h"
#include "../analysis/storage/storage.h"
#include "../common/array.h"
#include "../glibext/objhole.h"



/* Indique l'encodage d'une instruction de façon détaillée. */
typedef const char * (* get_instruction_encoding_fc) (const GArchInstruction *);

/* Fournit le nom humain de l'instruction manipulée. */
typedef const char * (* get_instruction_keyword_fc) (GArchInstruction * );

/* Complète un désassemblage accompli pour une instruction. */
typedef void (* call_instruction_hook_fc) (GArchInstruction *, InstrProcessHook, GArchProcessor *, GProcContext *, GExeFormat *);

/* Construit un petit résumé concis de l'instruction. */
typedef char * (* build_instruction_tooltip_fc) (const GArchInstruction *);

/* Fournit une description pour l'instruction manipulée. */
typedef const char * (* get_instruction_desc_fc) (const GArchInstruction *);

/* Charge une instruction depuis une mémoire tampon. */
typedef bool (* unserialize_instruction_fc) (GArchInstruction *, GAsmStorage *, GBinFormat *, packed_buffer_t *);

/* Sauvegarde une instruction dans une mémoire tampon. */
typedef bool (* serialize_instruction_fc) (GArchInstruction *, GAsmStorage *, packed_buffer_t *);

/* Ajoute à un tampon GLib le contenu de l'instance spécifiée. */
typedef GBufferLine * (* print_instruction_fc) (const GArchInstruction *, GBufferLine *, size_t, size_t, const GBinContent *);

/* Liste les registres lus et écrits par l'instruction. */
typedef void (* get_instruction_rw_regs_fc) (const GArchInstruction *, GArchRegister ***, size_t *, GArchRegister ***, size_t *);

/* Charge un contenu depuis une mémoire tampon. */
typedef bool (* load_instruction_fc) (GArchInstruction *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
typedef bool (* store_instruction_fc) (GArchInstruction *, GObjectStorage *, packed_buffer_t *);



/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _instr_extra_data_t
{
    itid_t uid;                             /* Identifiant unique du type  */

    ArchInstrFlag flags;                    /* Informations complémentaires*/

} instr_extra_data_t;

/* Informations glissées dans la structure GObject de GArchInstruction */
typedef union _instr_obj_extra_t
{
    instr_extra_data_t data;                /* Données embarquées          */
    lockable_obj_extra_t lockable;          /* Gestion d'accès aux fanions */

} instr_obj_extra_t;


/* Définition générique d'une instruction d'architecture (instance) */
struct _GArchInstruction
{
    GObject parent;                         /* A laisser en premier        */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

    /**
     * L'inclusion des informations suivantes dépend de l'architecture.
     *
     * Si la structure GObject possède un trou, on remplit de préférence
     * ce dernier.
     */

    instr_obj_extra_t extra;                /* Externalisation embarquée   */

#endif

    mrange_t range;                         /* Emplacement en mémoire      */

    flat_array_t *operands;                 /* Liste des opérandes         */

    /**
     * Il existe le besoin indéniable d'un verrou pour les accès aux instructions
     * liées. Il faut par ailleurs un verrou distinct pour les sources et les
     * destinations car une même instruction peut boucler sur elle même et la
     * fonction g_arch_instruction_change_link() pose des verrous sur les
     * deux extrémités.
     *
     * La GLib propose les fonctions g_bit_lock() / g_bit_unlock(), légères mais
     * sans distinction entre lectures et écritures. Tant pis : la réduction de
     * l'empreinte mémoire prime !
     *
     * Par contre la documentation indique :
     *
     * """
     * Attempting to lock on two different bits within the same integer is not supported.
     * """
     *
     * Donc on doit bien conserver un compteur distinct pour chaque extrémité.
     * Cela correspond de toute façon à la définition optimisée des tableaux
     * suivante.
     */

    flat_array_t *from;                     /* Origines des références     */
    flat_array_t *to;                       /* Instructions visées         */

};

/* Définition générique d'une instruction d'architecture (classe) */
struct _GArchInstructionClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_instruction_encoding_fc get_encoding; /* Obtention de l'encodage   */
    get_instruction_keyword_fc get_keyword; /* Texte humain équivalent     */
    call_instruction_hook_fc call_hook;     /* Décrochages éventuels       */
    build_instruction_tooltip_fc build_tooltip; /* Construction d'une bulle*/
    get_instruction_desc_fc get_desc;       /* Description assez complète  */

    unserialize_instruction_fc unserialize; /* Chargement depuis un tampon */
    serialize_instruction_fc serialize;     /* Conservation dans un tampon */

    print_instruction_fc print;             /* Imprime l'ensemble          */

    load_instruction_fc load;               /* Chargement depuis un tampon */
    store_instruction_fc store;             /* Conservation dans un tampon */

    //get_instruction_rw_regs_fc get_rw_regs; /* Liste des registres liés    */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_ARCH_INSTR_EXTRA(ins) (instr_extra_data_t *)&ins->extra

#else

#   define GET_ARCH_INSTR_EXTRA(ins) GET_GOBJECT_EXTRA(G_OBJECT(ins), instr_extra_data_t)

#endif


/**
 * Fournit une marge pour toutes les instructions particulières communes
 * à l'ensemble des architectures (GRawInstruction, GUndefInstruction).
 */

#define INSTR_TYPE_ID_OFFSET 5



#endif  /* _ARCH_INSTRUCTION_INT_H */
